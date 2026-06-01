include <lib/generated_constants.scad>

module relief_valve_block() {
  difference() {
    cube([80, 50, 40]);
    translate([15, 15, 10]) cube([50, 20, 25]);
    translate([40, 25, -1]) cylinder(h=45, d=12, $fn=24);
    translate([10, 25, 40]) cylinder(h=15, d=18, $fn=32);
  }
  translate([5, 5, 35])
    linear_extrude(2)
      text(str("RV ", delta_P_bar, " bar"), size=5);
}
relief_valve_block();
