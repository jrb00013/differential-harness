include <lib/generated_constants.scad>

module mount_rail() {
  for (y = [80, frame_W - 120])
    translate([100, y, 100])
      cube([frame_L - 200, 40, 15]);
}
mount_rail();
