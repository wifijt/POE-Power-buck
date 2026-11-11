# Case for the FRC PoE 12 V board

A tough two-piece PETG case: a tray the board drops into, and a lid held on with two M3 screws.

![print layout](../docs/case_print_layout.png)

| | |
|---|---|
| Outside (tray + lid) | 42.8 x 56.3 x 19.8 mm, 75.5 mm wide across the mounting ears |
| Walls / floor / lid | 3.0 / 2.4 / 2.8 mm, 3 mm corner radius |
| Robot mounting | 2 ears, #10 clearance holes (5.3 mm) **2.5" apart** (FRC ½" hole grid), 4 mm thick with gussets. Two zip-tie slots in the floor as a backup |
| Lid fixing | 2x M3 x 10 screws into brass M3 heat-set inserts (4.0 mm holes) |
| Board retention | Board sits on a 1.2 mm ledge 4 mm off the floor (room for the WAGO pins). Five posts on the lid clamp it from above, landing only on bare board edge |
| Openings | Front open over both WAGO terminals so wires go straight in. Lid open above them so the levers can be flipped. LED window, vents over the FETs and inductor, side vents |

## Files

* `case_tray.stl`, `case_lid.stl`: ready for PrusaSlicer. The lid is already flipped flat-side down.
* `case.scad`: the parametric OpenSCAD source. Wall thickness, clearances, ear spacing and the
  insert hole size are all variables at the top. Export one part with
  `openscad -D 'part="tray"' -o case_tray.stl case.scad`.

## Printing on the Prusa MK4

* **Material**: PETG is the tough, easy choice. For more impact and heat resistance, use Prusament
  PC Blend or ASA, but those want an enclosure to avoid warping.
* 0.4 mm nozzle, 0.2 mm layers, **6 perimeters**, 5 top / 5 bottom layers, **40 % gyroid** infill.
* No supports. Print the tray floor-down and the lid as exported (outer face on the sheet).
* Both parts fit on the sheet together.

## Hardware

* 2x M3 heat-set inserts (M3 x 5.7 mm, for a 4.0 mm hole). Press them into the two bosses with
  a soldering iron.
* 2x M3 x 10 socket-head screws for the lid.
* 2x #10-32 bolts + nylock nuts to mount to the robot (or zip ties through the floor slots).
* No inserts? Set `pilot = 2.6` in `case.scad` and use M3 self-tapping screws instead.

## Assembly

1. Solder the WAGO terminals onto the board first.
2. Drop the board into the tray with the terminals at the open front. The terminal faces sit
   flush with the opening.
3. Fit the lid. Its lip drops inside the walls and the posts press the board onto the ledge.
4. Screw the lid down, then mount the case to the robot.

## Notes

* I couldn't get the WAGO 2604-3102's exact height. The lid is open above the terminals, so any
  height fits.
* Covered parts get 9 mm of headroom; the tallest are the 7.7 mm bulk capacitors and the inductor.
* The lid's thin side arms beside the terminal opening are the weakest point. If you crack one,
  raise `lid_t` or print in PC Blend.
