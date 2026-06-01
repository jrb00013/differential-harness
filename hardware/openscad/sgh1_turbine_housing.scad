// Micro-hydro / Pelton test housing
include <lib/generated_constants.scad>

module turbine_housing() {
  difference() {
    union() {
      cylinder(h=40, d=100, $fn=60);
      translate([0, 0, 40]) cylinder(h=30, d=60, $fn=48);
    }
    translate([0, 0, 15]) cylinder(h=60, d=12, $fn=32);
    translate([35, 0, 25]) rotate([0, -90, 0]) cylinder(h=30, d=8, $fn=24);
    // nozzle jet from draw manifold
    translate([-35, 0, 30]) rotate([0, 90, 0]) cylinder(h=20, d=6, $fn=24);
  }
}
turbine_housing();
