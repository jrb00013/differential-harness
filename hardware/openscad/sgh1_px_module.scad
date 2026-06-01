// Pressure exchanger / work recovery module (simplified body)
include <lib/generated_constants.scad>
include <lib/utils.scad>

module px_module() {
  L = 180; W = 120; H = 90;
  difference() {
    translate([-L/2, -W/2, 0]) cube([L, W, H]);
    translate([-L/2+10, -W/2+10, 10]) cube([L-20, W-20, H]);
    // HP draw in
    translate([L/2-8, 0, H/2]) rotate([0,90,0]) cylinder(h=25, d=28, $fn=40);
    // LP out
    translate([-L/2+8, 0, H/2]) rotate([0,-90,0]) cylinder(h=25, d=28, $fn=40);
    // brine low pressure return
    translate([0, W/2-8, H-15]) rotate([90,0,0]) cylinder(h=20, d=22, $fn=32);
  }
}
px_module();
