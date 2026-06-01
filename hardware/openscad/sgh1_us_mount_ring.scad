// Ultrasonic transducer clamp for feed manifold
module us_mount_ring() {
  difference() {
    cylinder(h=18, d=55, $fn=48);
    translate([0, 0, 4]) cylinder(h=18, d=45, $fn=48);
  }
  translate([0, 25, 9]) cube([8, 15, 6], center=true);
}
us_mount_ring();
