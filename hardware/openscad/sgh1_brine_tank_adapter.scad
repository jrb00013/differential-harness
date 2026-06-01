module brine_tank_adapter() {
  difference() {
    union() {
      cylinder(h=30, d=70, $fn=48);
      translate([0, 0, 30]) cylinder(h=20, d=100, $fn=48);
    }
    translate([0, 0, 12]) cylinder(h=50, d=55, $fn=48);
    translate([-35, 0, 35]) rotate([0,-90,0]) cylinder(h=50, d=28, $fn=32);
    translate([35, 0, 35]) rotate([0,90,0]) cylinder(h=50, d=28, $fn=32);
  }
}
brine_tank_adapter();
