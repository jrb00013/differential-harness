// CHORUS-SGH-1 FULL ASSEMBLY
include <lib/generated_constants.scad>

use <sgh1_skid_frame.scad>
use <sgh1_membrane_housing.scad>
use <sgh1_manifold_feed.scad>
use <sgh1_manifold_draw.scad>
use <chorus_skid_enclosure.scad>
use <chorus_aeh_panel.scad>
use <sgh1_pump_mount.scad>

x0 = frame_L/2 - housing_len/2 - 80;
y0 = frame_W/2;
z0 = 120;

translate([-frame_L/2, -frame_W/2, 0])
  skid_frame();

translate([x0, y0, z0]) {
  housing_shell();
  translate([-housing_len/2 - 60, 0, housing_od/4])
    feed_manifold();
  translate([housing_len/2 + 60, 0, housing_od/4])
    draw_manifold();
}

translate([x0, y0, z0])
  chorus_enclosure();

translate([frame_L - 120, 40, 200])
  rotate([0, 90, 0])
    aeh_panel();

translate([80, frame_W/2 - 100, 40])
  pump_mount();
