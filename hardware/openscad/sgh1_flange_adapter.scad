// 2 inch tri-clamp style flange (51 mm)
module flange_adapter() {
  difference() {
    cylinder(h=12, d=64, $fn=64);
    translate([0, 0, 4]) cylinder(h=12, d=51, $fn=64);
    translate([0, 0, -1]) cylinder(h=8, d=22, $fn=32);
  }
  for (a = [0:45:315])
    rotate([0, 0, a]) translate([28, 0, 6]) cylinder(h=12, d=6.6, $fn=16);
}
flange_adapter();
