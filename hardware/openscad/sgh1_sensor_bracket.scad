// CHORUS-SGH-1 — DAQ / conductivity sensor bracket
include <lib/generated_constants.scad>

module sensor_bracket() {
  difference() {
    union() {
      cube([60, 40, 80]);
      translate([60, 20, 40])
        rotate([0, 90, 0])
          cylinder(h=30, d=40, center=true, $fn=48);
    }
    translate([10, 10, 10])
      cube([40, 25, 60]);
    translate([15, -1, 50])
      cylinder(h=42, d=12, $fn=24);
    translate([45, 20, -1])
      cylinder(h=10, d=6, $fn=20);
  }
}

sensor_bracket();
