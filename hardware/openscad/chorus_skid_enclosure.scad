// CHORUS — thermal / moist coupling plenum (wraps PRO housing)
include <lib/generated_constants.scad>

module chorus_enclosure() {
  plenum_gap = 25;
  wall = 4;
  len = housing_len + 80;
  od = housing_od + 2*plenum_gap;
  difference() {
    translate([0, 0, 30])
      cylinder(h=len, d=od, $fn=80);
    translate([0, 0, 30+wall])
      cylinder(h=len, d=od-2*wall, $fn=72);
    // humidity inlet louvers
    for (z = [60:40:len]) {
      rotate([0, 0, 30])
        translate([od/2-2, 0, z])
          cube([10, 40, 8], center=true);
    }
    // PV/moist panel mount rail (top)
    translate([-od/2, -30, len+20])
      cube([od, 60, 8]);
  }
  // sensor gland plate
  translate([od/2+5, 0, len/2+30])
    cube([8, 80, 40], center=true);
}

module chorus_enclosure_part() { chorus_enclosure(); }
chorus_enclosure_part();
