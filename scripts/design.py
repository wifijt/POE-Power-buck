"""Single source of truth for the FRC PoE-switch buck-boost board.

Every part, its value, footprint, MPN and pin->net map lives here.
gen_sch.py draws the schematic from it, gen_pcb.py builds the board from it,
gen_fab.py writes the JLC BOM/CPL from the finished board.

Design values follow two published TPS552882 / TPS55288 designs whose
values were cross-checked: a 12 V output stage (EwoudVV/ducktop2) and a
16 A booster (mikegoelzer/Homebrew-ECP5-SBC, pd-booster-16amps).
  Vref (FB)       = 1.2 V      (ref designs: 102k/11.3k -> 12.03 V; here 100k/11k -> 12.1 V)
  FSW  49.9k      = 400 kHz
  ILIM 26.7k      ~ 12.4 A average inductor current limit
  MODE tied to GND = internal VCC LDO, forced PWM
  EN/UVLO rising  = 1.23 V * (1 + Rtop/Rbot)
"""

PROJECT = "frc-poe-buckboost"

# lib_id, value, footprint, {pin: net}, mpn, description
FET = "frc_poe:NexFET_SON-8_3.3x3.3mm"
WAGO = "frc_poe:WAGO_2604-3102_1x02_P5.00mm"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
R0402 = "Resistor_SMD:R_0402_1005Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
CPOL = "Capacitor_SMD:CP_Elec_6.3x7.7"

PARTS = [
    # ---- connectors -------------------------------------------------------
    dict(ref="J1", sym="Connector:Screw_Terminal_01x02", value="IN 6-16V (WAGO 2604-3102)",
         fp=WAGO, pins={"1": "VIN", "2": "GND_IN"}, mpn="WAGO 2604-3102",
         desc="PCB terminal block, lever, 2-pole, 5.0 mm, 4 mm2 / 12 AWG", lcsc="", tht=True),
    dict(ref="J2", sym="Connector:Screw_Terminal_01x02", value="OUT 12V (WAGO 2604-3102)",
         fp=WAGO, pins={"1": "VOUT", "2": "GND"}, mpn="WAGO 2604-3102",
         desc="PCB terminal block, lever, 2-pole, 5.0 mm, 4 mm2 / 12 AWG", lcsc="", tht=True),
    # ---- reverse-polarity protection (low-side N-FET) + surge ---------------
    dict(ref="Q3", sym="Transistor_FET:CSD17577Q3A", value="CSD17577Q3A", fp=FET,
         pins={"1": "GND", "2": "GND", "3": "GND", "4": "Q3G", "5": "GND_IN"},
         lcsc="C201632", mpn="CSD17577Q3A", desc="30V N-MOSFET, SON3x3 - reverse-polarity switch"),
    dict(ref="R12", sym="Device:R", value="10k", fp=R0402, pins={"1": "VIN", "2": "Q3G"},
         lcsc="C25744", mpn="0402WGF1002TCE", desc="10k 1% 0402"),
    dict(ref="R13", sym="Device:R", value="100k", fp=R0402, pins={"1": "Q3G", "2": "GND"},
         lcsc="C25741", mpn="0402WGF1003TCE", desc="100k 1% 0402"),
    dict(ref="D3", sym="Device:D_Zener", value="BZT52C12", fp="Diode_SMD:D_SOD-123",
         pins={"1": "Q3G", "2": "GND"}, lcsc="C19077410", mpn="BZT52C12", desc="12V zener, SOD-123 - Q3 gate clamp"),
    dict(ref="D1", sym="Device:D_Zener", value="SMBJ16A", fp="Diode_SMD:D_SMB",
         pins={"1": "VIN", "2": "GND"}, lcsc="C19077571", mpn="SMBJ16A", desc="TVS 16V standoff unidirectional, SMB"),
    # ---- input capacitors ---------------------------------------------------
    dict(ref="C1", sym="Device:C_Polarized", value="100uF 35V hybrid", fp=CPOL,
         pins={"1": "VIN", "2": "GND"}, lcsc="C454360", mpn="EEH-ZK1V101XP",
         desc="100uF 35V polymer-hybrid, 6.3x7.7 (input bulk / damping)"),
    *[dict(ref=f"C{n}", sym="Device:C", value="10uF 50V X5R", fp=C1206,
           pins={"1": "VIN", "2": "GND"}, lcsc="C13585", mpn="CL31A106KBHNNNE", desc="10uF 50V X5R 1206")
      for n in (2, 3, 4, 5)],
    dict(ref="C7", sym="Device:C", value="100nF 50V", fp=C0402, pins={"1": "VIN", "2": "GND"},
         lcsc="C307331", mpn="CL05B104KB54PNC", desc="100nF 50V X7R 0402"),
    # ---- buck leg (external FETs) -------------------------------------------
    dict(ref="Q1", sym="Transistor_FET:CSD17577Q3A", value="CSD17577Q3A", fp=FET,
         pins={"1": "SW1", "2": "SW1", "3": "SW1", "4": "HSG", "5": "VIN"},
         lcsc="C201632", mpn="CSD17577Q3A", desc="30V N-MOSFET, SON3x3 - buck high side"),
    dict(ref="Q2", sym="Transistor_FET:CSD17577Q3A", value="CSD17577Q3A", fp=FET,
         pins={"1": "GND", "2": "GND", "3": "GND", "4": "LSG", "5": "SW1"},
         lcsc="C201632", mpn="CSD17577Q3A", desc="30V N-MOSFET, SON3x3 - buck low side"),
    dict(ref="R1", sym="Device:R", value="1R", fp=R0402, pins={"1": "DR1H", "2": "HSG"},
         lcsc="C25086", mpn="0402WGF100KTCE", desc="1R 1% 0402 gate resistor"),
    dict(ref="R2", sym="Device:R", value="1R", fp=R0402, pins={"1": "DR1L", "2": "LSG"},
         lcsc="C25086", mpn="0402WGF100KTCE", desc="1R 1% 0402 gate resistor"),
    dict(ref="L1", sym="Device:L", value="6.8uH 20A", fp="Inductor_SMD:L_TaiTech_TMPC1265_13.5x12.5mm",
         pins={"1": "SW1", "2": "SW2"}, lcsc="C41422303", mpn="ZEMS1265-6R8M",
         desc="6.8uH molded, Isat 20A, Irms 12.5A, 14mOhm, 1265 size"),
    dict(ref="C8", sym="Device:C", value="100nF 50V", fp=C0402, pins={"1": "BOOT1", "2": "SW1"},
         lcsc="C307331", mpn="CL05B104KB54PNC", desc="100nF 50V X7R 0402 bootstrap"),
    dict(ref="C9", sym="Device:C", value="100nF 50V", fp=C0402, pins={"1": "BOOT2", "2": "SW2"},
         lcsc="C307331", mpn="CL05B104KB54PNC", desc="100nF 50V X7R 0402 bootstrap"),
    # ---- controller -----------------------------------------------------------
    dict(ref="U1", sym="frc_poe:TPS552882", value="TPS552882RPMR",
         fp="frc_poe:TI_RPM0026A_VQFN-HR-26_4x3.5mm",
         pins={"1": "DR1L", "2": "DR1H", "3": "VIN", "4": "EN", "5": None, "6": None,
               "7": "DITH", "8": "FSW", "9": "GND", "10": "GND", "11": "VOUT", "12": "VOUT",
               "13": "VOUT", "14": "FB", "15": "GND", "16": None, "17": "ILIM", "18": "COMP",
               "19": "VCC", "20": "BOOT2", "21": "SW2", "22": "BOOT1", "23": "SW1",
               "24": "GND", "25": "SW2", "26": "VOUT"},
         lcsc="C3188898", mpn="TPS552882RPMR", desc="36V 16A buck-boost controller, standalone (no I2C)"),
    dict(ref="R3", sym="Device:R", value="100k", fp=R0402, pins={"1": "VIN", "2": "EN"},
         lcsc="C25741", mpn="0402WGF1003TCE", desc="100k 1% 0402 UVLO top"),
    dict(ref="R4", sym="Device:R", value="26.1k", fp=R0402, pins={"1": "EN", "2": "GND"},
         lcsc="C25875", mpn="0402WGF2612TCE", desc="26.1k 1% 0402 UVLO bottom (~5.9V rising)"),
    dict(ref="C11", sym="Device:C", value="10nF", fp=C0402, pins={"1": "DITH", "2": "GND"},
         lcsc="C15195", mpn="CL05B103KB5NNNC", desc="10nF 0402 spread-spectrum dither"),
    dict(ref="R5", sym="Device:R", value="49.9k", fp=R0402, pins={"1": "FSW", "2": "GND"},
         lcsc="C137969", mpn="RC0402FR-0749K9L", desc="49.9k 1% 0402 -> 400 kHz"),
    dict(ref="R6", sym="Device:R", value="100k", fp=R0402, pins={"1": "VOUT", "2": "FB"},
         lcsc="C25741", mpn="0402WGF1003TCE", desc="100k 1% 0402 FB top"),
    dict(ref="R7", sym="Device:R", value="11k", fp=R0402, pins={"1": "FB", "2": "GND"},
         lcsc="C25749", mpn="0402WGF1102TCE", desc="11k 1% 0402 FB bottom -> 12.1 V"),
    dict(ref="R9", sym="Device:R", value="26.7k", fp=R0402, pins={"1": "ILIM", "2": "GND"},
         lcsc="C4198231", mpn="CRCW040226K7FKEDC", desc="26.7k 1% 0402 -> ~12.4 A inductor limit"),
    dict(ref="R10", sym="Device:R", value="15k", fp=R0402, pins={"1": "COMP", "2": "COMP_RC"},
         lcsc="C25756", mpn="0402WGF1502TCE", desc="15k 1% 0402 compensation"),
    dict(ref="C12", sym="Device:C", value="10nF", fp=C0402, pins={"1": "COMP_RC", "2": "GND"},
         lcsc="C15195", mpn="CL05B103KB5NNNC", desc="10nF 50V X7R 0402 compensation"),
    dict(ref="C13", sym="Device:C", value="100pF C0G", fp=C0402, pins={"1": "COMP", "2": "GND"},
         lcsc="C1546", mpn="0402CG101J500NT", desc="100pF 50V C0G 0402 compensation"),
    dict(ref="C14", sym="Device:C", value="22uF 25V", fp=C1206, pins={"1": "VCC", "2": "GND"},
         lcsc="C12891", mpn="CL31A226KAHNNNE", desc="22uF 25V X5R 1206 (VCC, needs >4.7uF effective)"),
    dict(ref="C15", sym="Device:C", value="100nF 50V", fp=C0402, pins={"1": "VCC", "2": "GND"},
         lcsc="C307331", mpn="CL05B104KB54PNC", desc="100nF 0402 VCC HF"),
    # ---- output ---------------------------------------------------------------
    *[dict(ref=f"C{n}", sym="Device:C", value="22uF 25V X7R", fp=C1210,
           pins={"1": "VOUT", "2": "GND"}, lcsc="C21397", mpn="GRM32ER71E226KE15L", desc="22uF 25V X7R 1210")
      for n in (16, 17, 18, 19)],
    dict(ref="C20", sym="Device:C_Polarized", value="100uF 35V hybrid", fp=CPOL,
         pins={"1": "VOUT", "2": "GND"}, lcsc="C454360", mpn="EEH-ZK1V101XP",
         desc="100uF 35V polymer-hybrid, 6.3x7.7 (output bulk, sets ESR zero)"),
    dict(ref="C21", sym="Device:C", value="100nF 50V", fp=C0402, pins={"1": "VOUT", "2": "GND"},
         lcsc="C307331", mpn="CL05B104KB54PNC", desc="100nF 50V X7R 0402"),
    dict(ref="R11", sym="Device:R", value="4.7k", fp=R0603, pins={"1": "VOUT", "2": "LED_A"},
         lcsc="C23162", mpn="0603WAF4701T5E", desc="4.7k 0603 LED resistor"),
    dict(ref="D2", sym="Device:LED", value="GREEN", fp="LED_SMD:LED_0603_1608Metric",
         pins={"1": "GND", "2": "LED_A"}, lcsc="C12624", mpn="KT-0603G", desc="Green LED 0603 - 12V output on"),
]

NO_CONNECT = {("U1", "5"), ("U1", "6"), ("U1", "16")}


def nets():
    out = {}
    for p in PARTS:
        for pin, n in p["pins"].items():
            if n:
                out.setdefault(n, []).append((p["ref"], pin))
    return out
