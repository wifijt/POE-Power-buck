// FRC PoE 12V buck-boost - 3D-printable case (tray + lid)
// Board: 36.0 x 57.0 x 1.6 mm with three M3 mounting holes (copper-free, r = 3.3 mm).
// The board is screwed down onto three standoffs (brass M3 heat-set inserts). Two support
// pillars sit under the WAGO 2604-3102 terminals, which take wires VERTICALLY from the top:
// pushing a lever or a wire presses the board onto them instead of flexing it.
// Lid: open above the terminals (wires leave upward, levers swing out over the open front).
// Built tough for a robot: 3 mm walls/floor/lid, standoffs fused into the walls,
// 4 lid screws, 4 braced mounting ears for #10 bolts.
// Prusa MK4: PETG (or Prusament PC Blend / ASA with an enclosure), 0.4 mm nozzle, 0.2 mm layers,
// 6 perimeters, 5 top/bottom layers, 40 % gyroid infill, no supports.
// Print the tray floor-down and the lid top-down (flat face on the sheet). Set part="tray" or "lid".

part = "both";            // "tray", "lid", "both" (both = print layout), "sticker" (2D lid sticker outline)

// ---- board -----------------------------------------------------------------
pcb_w = 36.0;  pcb_l = 57.0;  pcb_t = 1.6;
// board coords are KiCad coords: x right, y DOWN from the terminal edge.
function B(x, y) = [x, pcb_l - y];          // -> case coords (y up, terminal edge at top)
holes   = [[2.9, 3.4], [3.5, 53.4], [32.5, 53.4]];   // M3 mounting holes (gen_pcb.py)
pillars = [[12.9, 9.4], [27.4, 9.4]];               // between each WAGO's four pins (bottom side is bare)

// ---- case parameters -------------------------------------------------------
clr     = 0.5;    // board-to-wall clearance per side
wall    = 3.0;
floor_t = 3.0;
under   = 6.0;    // board underside above the floor (WAGO pin tails stick out ~2.4 mm)
above   = 9.0;    // headroom over the board top (tallest covered parts: 7.7 mm caps)
lid_t   = 3.0;
lip_h   = 2.4;    // lid lip that drops into the tray
lip_clr = 0.25;
lip_w   = 1.2;    // lip wall; keeps 0.6 mm from the C1 can (board x 34.45)

// standoffs: M3 x 8 screw from the top through the board into an M3 x 5.7 heat-set insert
so_top_d  = 8.0;  // flat top under the board (plastic on soldermask is fine)
so_base_d = 13.0; // flared foot
so_flare  = 3.5;  // height of the flare
insert_d  = 4.0;  insert_depth = 6.5;   // no inserts? insert_d = 2.6 and M3 self-tapping screws
pillar_d  = 5.0;  pillar_gap = 0.15;    // pillars sit just below the board

cav_w = pcb_w + 2*clr;   cav_l = pcb_l + 2*clr;
out_w = cav_w + 2*wall;  out_l = cav_l + 2*wall;
pcb_z  = floor_t + under;            // board underside
top_z  = pcb_z + pcb_t + above;      // tray rim = lid underside
bx0 = wall + clr;  by0 = wall + clr; // board origin in case coords
function C(p) = [bx0 + p[0], by0 + B(p[0], p[1])[1]];   // board xy -> case xy

// front opening over the WAGO bodies (board x 6.5-33.8); levers swing out through it
open_x0 = 5.8;  open_x1 = 34.4;
term_depth = 17.6;                   // terminal bodies end at board y 17.1

// lid screws: 4x M3 x 10 into M3 heat-set inserts in bosses on the side walls
boss = 9.0;  boss_ys = [20.0, 40.0];   // board y of each boss pair
// robot mounting: 4 ears, #10 clearance holes, 2.5" apart across
ear_hole = 5.3;  ear_pitch = 63.5;  ear_t = 6.0;  ear_ys = [4.0, 52.0];
// ear bracing: 3 mm gussets up the wall, kept clear of a #10 SAE washer (11.1 mm OD) under the bolt
gus_t = 3.0;  gus_h = 12.0;  gus_l = 6.5;  gus_dy = [4.5, 7.5];   // gusset y span from the hole centre
fillet = 3.0;   // 45-degree fillet along the ear root

module rounded_box(w, l, h, r=3.0) {
    hull() for (x=[r, w-r], y=[r, l-r]) translate([x, y, 0]) cylinder(r=r, h=h, $fn=32);
}
function boss_x(sx) = sx < 0 ? -boss/2 + 0.5 : out_w + boss/2 - 0.5;

module standoff(p) {
    translate([C(p)[0], C(p)[1], floor_t - 0.01]) {
        cylinder(d1=so_base_d, d2=so_top_d, h=so_flare, $fn=64);
        cylinder(d=so_top_d, h=under + 0.01, $fn=64);
    }
}

// mounting ear: plate fused to the wall from the case end to the next lid-screw boss, two gussets, root fillet
function ear_boss_y(cy) = let(bys = [for (y = boss_ys) by0 + B(0, y)[1]],
                              b = abs(bys[0] - cy) < abs(bys[1] - cy) ? bys[0] : bys[1])
                          b + (b > cy ? -boss/2 + 1 : boss/2 - 1);   // reach 1 mm into the boss
module ear(sx, cy) {
    cx = out_w/2 + sx*ear_pitch/2;
    wx = sx < 0 ? 0 : out_w;                     // wall face
    inward = cy < out_l/2 ? 1 : -1;              // toward the case middle
    y_end  = cy - inward*7.5;                    // case-end side of the root
    y_boss = ear_boss_y(cy);
    hull() {
        translate([cx, cy, 0]) cylinder(d=15, h=ear_t, $fn=48);   // full 15 mm width out to the hole: gussets sit on plate
        translate([wx - (sx < 0 ? 0 : 1), min(y_end, y_boss), 0]) cube([1, abs(y_boss - y_end), ear_t]);
    }
    // root fillet along the flat part of the wall (stops at the 3 mm corner radius); sunk 0.5 mm into
    // the wall and the plate so the union stays a clean solid
    f_y0 = min(y_end + inward*3, y_boss);  f_y1 = max(y_end + inward*3, y_boss);
    translate([wx - sx*0.5, f_y0, ear_t - 0.5]) rotate([-90, 0, 0])
        linear_extrude(f_y1 - f_y0) polygon([[0, 0], [sx*(fillet + 1), 0], [0, -(fillet + 1)]]);
    // gussets: triangles in the x-z plane, tall at the wall, ending gus_l out
    // sunk 1 mm into the wall: the case-end gusset sits where the 3 mm corner radius starts to curve away
    for (side = [-1, 1]) translate([wx - sx*1.0, side > 0 ? cy + gus_dy[1] : cy - gus_dy[0], ear_t - 0.5])
        rotate([90, 0, 0]) linear_extrude(gus_t) polygon([[0, 0], [sx*(gus_l + 1.0), 0], [0, gus_h + 0.5]]);
}

module tray() {
    difference() {
        union() {
            rounded_box(out_w, out_l, top_z);
            for (sx=[-1, 1], y=boss_ys)                         // lid screw bosses
                translate([boss_x(sx) - boss/2, by0 + B(0, y)[1] - boss/2, 0]) cube([boss, boss, top_z]);
            for (sx=[-1, 1], y=ear_ys) ear(sx, by0 + B(0, y)[1]);   // mounting ears
        }
        // cavity: full board footprint + clearance, floor to rim
        translate([wall, wall, floor_t]) cube([cav_w, cav_l, top_z]);
        // front opening for the WAGO terminals: from just above the board top to the rim
        translate([bx0 + open_x0, out_l - wall - 1, pcb_z + pcb_t - 0.4])
            cube([open_x1 - open_x0, wall + 2, top_z]);
        for (sx=[-1, 1], y=ear_ys)                              // ear holes
            translate([out_w/2 + sx*ear_pitch/2, by0 + B(0, y)[1], -1]) cylinder(d=ear_hole, h=ear_t + 2, $fn=40);
        for (sx=[-1, 1], y=boss_ys)                             // lid insert holes
            translate([boss_x(sx), by0 + B(0, y)[1], top_z - insert_depth]) cylinder(d=insert_d, h=top_z, $fn=32);
        for (sx=[0, 1], i=[0:2])                                // side vents beside the FETs / inductor
            translate([sx*(out_w - wall) - 0.5, by0 + B(0, 28 + i*3.5)[1] - 0.9, pcb_z + pcb_t + 2.5])
                cube([wall + 1, 1.8, 4.5]);
        for (y=[18, 40])                                        // zip-tie slots (backup mounting)
            translate([out_w/2 - 2.5, by0 + B(0, y)[1] - 2, -1]) cube([5, 4, floor_t + 2]);
    }
    // standoffs and pillars are added after the cavity cut
    difference() {
        union() {
            for (p = holes) standoff(p);
            // fuse each standoff into the nearest walls with a solid web
            for (p = holes) {
                c = C(p);
                wx = p[0] < pcb_w/2 ? wall - 0.01 : out_w - wall + 0.01;
                wy = p[1] < pcb_l/2 ? out_l - wall + 0.01 : wall - 0.01;
                hull() { translate([c[0], c[1], floor_t]) cylinder(d=so_top_d, h=under, $fn=48);
                         translate([min(c[0], wx) - (p[0] < pcb_w/2 ? 0.01 : 0), c[1] - so_top_d/2, floor_t])
                             cube([abs(wx - c[0]) + 0.01, so_top_d, under]); }
                hull() { translate([c[0], c[1], floor_t]) cylinder(d=so_top_d, h=under, $fn=48);
                         translate([c[0] - so_top_d/2, min(c[1], wy), floor_t])
                             cube([so_top_d, abs(wy - c[1]) + 0.01, under]); }
            }
            for (p = pillars) translate([C(p)[0], C(p)[1], floor_t - 0.01]) {
                cylinder(d1=pillar_d + 4, d2=pillar_d, h=2.5, $fn=48);
                cylinder(d=pillar_d, h=under - pillar_gap + 0.01, $fn=48);
            }
        }
        for (p = holes) translate([C(p)[0], C(p)[1], pcb_z - insert_depth]) cylinder(d=insert_d, h=insert_depth + 1, $fn=32);
    }
}

// ---- lid label ---------------------------------------------------------------
// Default: the lid top is flat and carries a full-size printed sticker, cut on a Silhouette (or similar)
// with holes for the vents, LED window, screws and terminal opening. scripts/gen_lid_sticker.py makes it
// from lid_sticker() below, so the sticker always matches the lid.
// lid_engrave = true engraves the +/- marks and text instead (0.6 mm deep; text >= 3 mm for a 0.4 nozzle).
lid_engrave   = false;
sticker_inset = 0.5;    // sticker edge sits this far inside the lid edge, and every hole grows by this much
label_depth = 0.6;
label_font  = "Liberation Sans:style=Bold";
// [pole x on the board, "+" or "-"]: J2 = OUT (10.4 +, 15.4 -), J1 = IN (24.9 +, 29.9 -)
poles = [[10.4, "+"], [15.4, "-"], [24.9, "+"], [29.9, "-"]];
pole_y = 20.4;   mark = 3.6;  bar = 1.2;                    // board y of the +/- marks, mark size
module engrave_at(p) translate([C(p)[0], C(p)[1], top_z + lid_t - label_depth]) linear_extrude(label_depth + 1) children();

module lid_label() if (lid_engrave) {
    for (q = poles) engrave_at([q[0], pole_y]) {
        square([mark, bar], center=true);
        if (q[1] == "+") square([bar, mark], center=true);
    }
    engrave_at([12.9, 24.6]) text("OUT",   size=3.6, font=label_font, halign="center", valign="center");
    engrave_at([12.9, 28.6]) text("12V",   size=3.0, font=label_font, halign="center", valign="center");
    engrave_at([27.4, 24.6]) text("IN",    size=3.6, font=label_font, halign="center", valign="center");
    engrave_at([27.4, 28.6]) text("6-16V", size=3.0, font=label_font, halign="center", valign="center");
    engrave_at([24.6, 32.8]) text("20A",   size=3.6, font=label_font, halign="center", valign="center");
    engrave_at([18.0, 51.6]) text("TURNER VISION",  size=3.2, font=label_font, halign="center", valign="center");
    engrave_at([18.0, 55.6]) text("POE BUCK BOOST", size=3.0, font=label_font, halign="center", valign="center");
}

// 2D sticker shape in case coordinates (assembled, seen from above): the lid's top face without the
// screw tabs, shrunk by sticker_inset, which also grows every hole by sticker_inset
module lid_sticker() offset(delta=-sticker_inset) intersection() {
    projection(cut=true) translate([0, 0, -(top_z + lid_t - 0.05)]) lid();
    hull() for (x=[3, out_w-3], y=[3, out_l-3]) translate([x, y]) circle(r=3, $fn=32);   // main top, no screw tabs
}

module lid() {
    // drawn in assembled orientation; lid underside at z = top_z
    difference() {
        union() {
            translate([0, 0, top_z]) rounded_box(out_w, out_l, lid_t);
            for (sx=[-1, 1], y=boss_ys)                         // tabs over the bosses
                translate([boss_x(sx) - boss/2, by0 + B(0, y)[1] - boss/2, top_z]) cube([boss, boss, lid_t]);
            // lip that drops into the tray (follows the cavity walls)
            difference() {
                translate([wall + lip_clr, wall + lip_clr, top_z - lip_h])
                    cube([cav_w - 2*lip_clr, cav_l - 2*lip_clr, lip_h]);
                translate([wall + lip_clr + lip_w, wall + lip_clr + lip_w, top_z - lip_h - 1])
                    cube([cav_w - 2*(lip_clr + lip_w), cav_l - 2*(lip_clr + lip_w), lip_h + 2]);
            }
            // stiffening rib across the lid, between the terminal opening and the vents
            translate([wall, by0 + B(0, term_depth + 3.5)[1] - 1.5, top_z - lip_h]) cube([cav_w, 3, lip_h]);
        }
        // open over the WAGO terminals so the levers and wires are reachable
        translate([bx0 + open_x0, by0 + B(0, term_depth)[1], top_z - lip_h - 1])
            cube([open_x1 - open_x0, out_l, lid_t + lip_h + 2]);
        // LED window (D2 at board 3.0, 22.7)
        translate([C([3.0, 22.7])[0], C([3.0, 22.7])[1], top_z - lip_h - 1]) cylinder(d=3.0, h=lid_t + lip_h + 2, $fn=24);
        // vent slots over the inductor and the FETs
        for (i=[0:5]) translate([bx0 + 9 + i*3.6, by0 + B(0, 49)[1], top_z - 1]) cube([1.6, 13, lid_t + 2]);
        // FET vents: two slots right of the IN / 20A text (board x 30.6-34.6, y 31-40), clear of the lid lip
        for (x=[30.6, 33.0]) translate([bx0 + x, by0 + B(0, 40)[1], top_z - 1]) cube([1.6, 9.0, lid_t + 2]);
        for (sx=[-1, 1], y=boss_ys)                             // lid screw holes (counterbored)
            translate([boss_x(sx), by0 + B(0, y)[1], top_z - 1]) {
                cylinder(d=3.4, h=lid_t + 2, $fn=24);
                translate([0, 0, lid_t - 0.8]) cylinder(d=6.2, h=2, $fn=32);
                // the lid prints face-down, so the plastic above each counterbore prints over air. Two
                // 0.2 mm bridge layers give it something to stand on: first a slot (bridged across),
                // then a square (bridged across the slot), then the round hole.
                translate([0, 0, lid_t - 0.8 - 0.2]) translate([-3.4/2, -6.2/2, 0]) cube([3.4, 6.2, 0.2 + 0.01]);
                translate([0, 0, lid_t - 0.8 - 0.4]) translate([-3.4/2, -3.4/2, 0]) cube([3.4, 3.4, 0.2 + 0.01]);
            }
        // label: polarity marks over each terminal pole, terminal names, branding
        lid_label();
    }
}

if (part == "tray") tray();
// lid flipped face-down for printing: a ROTATION about x (a mirror would print the text and the
// whole lid as a mirror image)
module lid_print() translate([0, out_l, top_z + lid_t]) rotate([180, 0, 0]) lid();
if (part == "tray") tray();
else if (part == "lid") lid_print();
else if (part == "sticker") lid_sticker();   // 2D: export as .svg / .dxf
else { tray(); translate([out_w + 30, 0, 0]) lid_print(); }
