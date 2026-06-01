// 50 L drum top adapter — feed (low sal)
module feed_tank_adapter() {
  difference() {
  union() {
    cylinder(h=25, d=60, $fn=48);
    translate([0, 0, 25]) cylinder(h=15, d=80, $fn=48);
  }
  translate([0, 0, 10]) cylinder(h=40, d=50, $fn=48);
  translate([30, 0, 30]) rotate([0,90,0]) cylinder(h=40, d=22, $fn=32);
  }
}
feed_tank_adapter();
