// FRC PoE 12V buck-boost - 3D-printable case (tray + lid)
// Board: 36.0 x 49.5 x 1.6 mm, no mounting holes. WAGO 2604-3102 terminals on the
// top board edge with wires entering through the open front; levers reachable through the lid cut-out.
// Built tough for a robot: 3 mm walls, braced ears, brass heat-set inserts for the lid.
// Prusa MK4: PETG (or Prusament PC Blend / ASA with an enclosure), 0.4 mm nozzle, 0.2 mm layers,
// 6 perimeters, 5 top/bottom layers, 40 % gyroid infill, no supports.
// Print the tray floor-down and the lid top-down (flat face on the sheet). Set part="tray" or "lid".

part = "both";            // "tray", "lid", "both" (both = print layout)

// ---- board -----------------------------------------------------------------
pcb_w = 36.0;  pcb_l = 49.5;  pcb_t = 1.6;
// board coords are KiCad coords: x right, y DOWN from the terminal edge.
function B(x, y) = [x, pcb_l - y];          // -> case coords (y up, terminal edge at top)

// ---- case parameters -------------------------------------------------------
clr     = 0.4;    // board-to-wall clearance per side
wall    = 3.0;
floor_t = 2.4;
under   = 4.0;    // gap under the board for through-hole pins (WAGO pins stick out ~2.5 mm)
ledge   = 1.2;    // width of the shelf the board rests on
above   = 9.0;    // headroom over the board top (tallest covered parts: 7.7 mm caps)
lid_t   = 2.8;
lip_h   = 2.4;    // lid lip that drops into the tray
lip_clr = 0.25;

cav_w = pcb_w + 2*clr;   cav_l = pcb_l + 2*clr;
out_w = cav_w + 2*wall;  out_l = cav_l + 2*wall;
pcb_z  = floor_t + under;            // board underside
top_z  = pcb_z + pcb_t + above;      // tray rim = lid underside
bx0 = wall + clr;  by0 = wall + clr; // board origin in case coords

// front opening over the WAGO bodies (board x 6.5-33.8)
open_x0 = 5.8;  open_x1 = 34.4;
term_depth = 17.6;                   // terminal bodies end at board y 17.2

// mounting: 2 ears, #10 clearance holes
ear_hole = 5.3;  ear_pitch = 63.5;  ear_y_board = 9.0;  ear_t = 4.0;   // holes 2.5" apart = FRC 1/2" grid
// lid screws: M3 x 10 into brass M3 heat-set inserts (4.0 mm hole, 5.7 mm long).
// No inserts? set pilot = 2.6 and use M3 self-tapping screws.
pilot = 4.0;  screw_clr = 3.4;  boss = 9.0;  boss_y_board = 40.0;

module rounded_box(w, l, h, r=3.0) {
    hull() for (x=[r, w-r], y=[r, l-r]) translate([x, y, 0]) cylinder(r=r, h=h, $fn=32);
}

module tray() {
    difference() {
        union() {
            rounded_box(out_w, out_l, top_z);
            // screw bosses on the left/right walls
            for (sx=[-1, 1]) {
                cx = sx < 0 ? -boss/2 + 0.5 : out_w + boss/2 - 0.5;
                translate([cx - boss/2, by0 + B(0, boss_y_board)[1] - boss/2, 0])
                    cube([boss, boss, top_z]);
            }
            // mounting ears
            for (sx=[-1, 1]) {
                cx = out_w/2 + sx*ear_pitch/2;
                hull() {
                    translate([cx, by0 + B(0, ear_y_board)[1], 0]) cylinder(d=12, h=ear_t, $fn=48);
                    translate([sx < 0 ? 0 : out_w - 1, by0 + B(0, ear_y_board)[1] - 7, 0]) cube([1, 14, ear_t]);
                }
                // triangular gussets bracing the ear to the wall
                for (dy=[-6, 4.5]) translate([sx < 0 ? -6 : out_w, by0 + B(0, ear_y_board)[1] + dy, ear_t])
                    rotate([90, 0, 0]) translate([0, 0, -1.5]) linear_extrude(1.5)
                        polygon(sx < 0 ? [[0,0],[6,0],[6,8]] : [[0,0],[6,0],[0,8]]);
            }
        }
        // cavity above the ledge (full board footprint + clearance)
        translate([wall, wall, pcb_z]) cube([cav_w, cav_l, top_z]);
        // cavity below the board, inset by the ledge
        translate([wall + ledge, wall + ledge, floor_t]) cube([cav_w - 2*ledge, cav_l - 2*ledge, top_z]);
        // front opening for the WAGO terminals: from just above the board top to the rim
        translate([bx0 + open_x0, out_l - wall - 1, pcb_z + pcb_t - 0.4])
            cube([open_x1 - open_x0, wall + 2, top_z]);
        // ear holes
        for (sx=[-1, 1]) translate([out_w/2 + sx*ear_pitch/2, by0 + B(0, ear_y_board)[1], -1])
            cylinder(d=ear_hole, h=ear_t + 2, $fn=40);
        // boss pilot holes
        for (sx=[-1, 1]) {
            cx = sx < 0 ? -boss/2 + 0.5 : out_w + boss/2 - 0.5;
            translate([cx, by0 + B(0, boss_y_board)[1], floor_t + 2]) cylinder(d=pilot, h=top_z, $fn=24);
        }
        // side vents below the lid, beside the inductor/FETs
        for (sx=[0, 1]) for (i=[0:3])
            translate([sx*(out_w - wall) - 0.5, by0 + B(0, 30 + i*4)[1] - 0.9, pcb_z + pcb_t + 2.5])
                cube([wall + 1, 1.8, 4.5]);
        // zip-tie slots in the floor (alternative mounting)
        for (y=[16, 36]) translate([out_w/2 - 2.5, by0 + B(0, y)[1] - 2, -1]) cube([5, 4, floor_t + 2]);
    }
}

module lid() {
    // drawn in assembled orientation; lid underside at z = top_z
    difference() {
        union() {
            translate([0, 0, top_z]) rounded_box(out_w, out_l, lid_t);
            // tabs over the bosses
            for (sx=[-1, 1]) {
                cx = sx < 0 ? -boss/2 + 0.5 : out_w + boss/2 - 0.5;
                translate([cx - boss/2, by0 + B(0, boss_y_board)[1] - boss/2, top_z]) cube([boss, boss, lid_t]);
            }
            // lip that drops into the tray (follows the cavity, skips the terminal opening)
            difference() {
                translate([wall + lip_clr, wall + lip_clr, top_z - lip_h])
                    cube([cav_w - 2*lip_clr, cav_l - 2*lip_clr, lip_h]);
                translate([wall + lip_clr + 1.2, wall + lip_clr + 1.2, top_z - lip_h - 1])
                    cube([cav_w - 2*lip_clr - 2.4, cav_l - 2*lip_clr - 2.4, lip_h + 2]);
            }
            // posts that clamp the board down at parts-free spots on the edge
            for (p=[[0.6, 10], [0.6, 30], [0.6, 37.5], [35.4, 19.0], [35.4, 47.2]])
                translate([bx0 + p[0], by0 + B(p[0], p[1])[1], pcb_z + pcb_t])
                    cylinder(d=3.0, h=top_z - (pcb_z + pcb_t) + 0.1, $fn=24);
        }
        // open over the WAGO terminals so the levers and wires are reachable
        translate([bx0 + open_x0, by0 + B(0, term_depth)[1], top_z - lip_h - 1])
            cube([open_x1 - open_x0, out_l, lid_t + lip_h + 2]);
        // LED window (D2 at board 3.0, 22.7)
        translate([bx0 + 3.0, by0 + B(0, 22.7)[1], top_z - 1]) cylinder(d=3.0, h=lid_t + 2, $fn=24);
        // vent slots over the FETs and inductor
        for (i=[0:5]) translate([bx0 + 9 + i*3.6, by0 + B(0, 47)[1], top_z - 1]) cube([1.6, 16, lid_t + 2]);
        for (i=[0:3]) translate([bx0 + 17 + i*3.6, by0 + B(0, 29.5)[1], top_z - 1]) cube([1.6, 8.5, lid_t + 2]);
        // screw holes
        for (sx=[-1, 1]) {
            cx = sx < 0 ? -boss/2 + 0.5 : out_w + boss/2 - 0.5;
            translate([cx, by0 + B(0, boss_y_board)[1], top_z - 1]) cylinder(d=screw_clr, h=lid_t + 2, $fn=24);
        }
        // label
        translate([bx0 + 2.0, by0 + B(0, 34)[1], top_z + lid_t - 0.6]) rotate([0, 0, 90])
            linear_extrude(1) text("12V PoE", size=3.2, font="Liberation Sans:style=Bold");
    }
}

if (part == "tray") tray();
else if (part == "lid") translate([0, 0, top_z + lid_t]) mirror([0, 0, 1]) lid();   // flipped for printing
else { tray(); translate([out_w + 22, 0, top_z + lid_t]) mirror([0, 0, 1]) lid(); }
