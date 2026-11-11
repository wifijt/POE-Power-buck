// FRC PoE 12V buck-boost - 3D-printable case (tray + lid)
// Board: 36.0 x 57.0 x 1.6 mm with three M3 mounting holes (copper-free, r = 3.3 mm).
// The board is screwed down onto three standoffs (brass M3 heat-set inserts). Two support
// pillars sit under the WAGO 2604-3102 terminals, which take wires VERTICALLY from the top:
// pushing a lever or a wire presses the board onto them instead of flexing it.
// Lid: open above the terminals (wires leave upward, levers swing out over the open front).
// Built tough for a robot: 3 mm walls/floor/lid, standoffs fused into the walls,
// 4 lid screws, 4 braced mounting ears on the FRC 1/2" grid.
// Prusa MK4: PETG (or Prusament PC Blend / ASA with an enclosure), 0.4 mm nozzle, 0.2 mm layers,
// 6 perimeters, 5 top/bottom layers, 40 % gyroid infill, no supports.
// Print the tray floor-down and the lid top-down (flat face on the sheet). Set part="tray" or "lid".

part = "both";            // "tray", "lid", "both" (both = print layout)

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
// robot mounting: 4 ears, #10 clearance holes, 2.5" apart across, on the 1/2" grid
ear_hole = 5.3;  ear_pitch = 63.5;  ear_t = 5.0;  ear_ys = [4.0, 52.0];

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

module tray() {
    difference() {
        union() {
            rounded_box(out_w, out_l, top_z);
            for (sx=[-1, 1], y=boss_ys)                         // lid screw bosses
                translate([boss_x(sx) - boss/2, by0 + B(0, y)[1] - boss/2, 0]) cube([boss, boss, top_z]);
            for (sx=[-1, 1], y=ear_ys) {                        // mounting ears
                cx = out_w/2 + sx*ear_pitch/2;  cy = by0 + B(0, y)[1];
                hull() {
                    translate([cx, cy, 0]) cylinder(d=13, h=ear_t, $fn=48);
                    translate([sx < 0 ? 0 : out_w - 1, cy - 7.5, 0]) cube([1, 15, ear_t]);
                }
                for (dy=[-7.5, 6.0]) translate([sx < 0 ? -8 : out_w, cy + dy, ear_t])   // gussets
                    rotate([90, 0, 0]) translate([0, 0, -1.5]) linear_extrude(1.5)
                        polygon(sx < 0 ? [[0,0],[8,0],[8,9]] : [[0,0],[8,0],[0,9]]);
            }
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
        for (i=[0:3]) translate([bx0 + 17 + i*3.6, by0 + B(0, 33)[1], top_z - 1]) cube([1.6, 8.5, lid_t + 2]);
        for (sx=[-1, 1], y=boss_ys)                             // lid screw holes (counterbored)
            translate([boss_x(sx), by0 + B(0, y)[1], top_z - 1]) {
                cylinder(d=3.4, h=lid_t + 2, $fn=24);
                translate([0, 0, lid_t - 0.8]) cylinder(d=6.2, h=2, $fn=32);
            }
        // label
        translate([C([1.6, 44])[0], C([1.6, 44])[1], top_z + lid_t - 0.6]) rotate([0, 0, 90])
            linear_extrude(1) text("12V PoE", size=3.2, font="Liberation Sans:style=Bold");
    }
}

if (part == "tray") tray();
else if (part == "lid") translate([0, 0, top_z + lid_t]) mirror([0, 0, 1]) lid();   // flipped for printing
else { tray(); translate([out_w + 30, 0, top_z + lid_t]) mirror([0, 0, 1]) lid(); }
