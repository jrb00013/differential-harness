// v2 RED nanopore cartridge — same flange as PRO housing
include <lib/generated_constants.scad>

module red_cartridge_v2() {
  difference() {
    cylinder(h=housing_len*0.8, d=housing_od - 24, $fn=72);
    translate([0, 0, 8]) cylinder(h=housing_len, d=housing_od - 50, $fn=64);
    // nanopore field pattern (visual)
    for (z = [20:15:housing_len*0.6])
      for (a = [0:30:330])
        rotate([0, 0, a]) translate([housing_od/2 - 30, 0, z])
          cylinder(h=3, d=2, $fn=8);
  }
}
red_cartridge_v2();
