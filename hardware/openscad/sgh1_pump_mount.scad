// CHORUS-SGH-1 — feed pump + prefilter mount plate
include <lib/generated_constants.scad>

module pump_mount() {
  plate_w = 280;
  plate_h = 200;
  plate_t = 8;
  difference() {
    cube([plate_w, plate_t, plate_h]);
    // pump footprint
    translate([plate_w/2, plate_t/2, plate_h/2])
      cube([120, plate_t+2, 100], center=true);
    translate([40, plate_t/2, plate_h-40])
      cylinder(h=plate_t+2, d=80, center=true, $fn=48);
    for (x = [25, plate_w-25])
      translate([x, -1, 25])
        cylinder(h=plate_t+2, d=7, $fn=20);
  }
}

module pump_mount_part() { pump_mount(); }
pump_mount_part();
