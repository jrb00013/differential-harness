include <lib/generated_constants.scad>

module drip_tray() {
  L = frame_L - 40;
  W = frame_W - 40;
  translate([20, 20, 25])
  difference() {
    cube([L, W, 8]);
    translate([8, 8, 2]) cube([L-16, W-16, 10]);
  }
}
drip_tray();
