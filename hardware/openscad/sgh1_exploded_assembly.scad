// Exploded assembly for documentation / STL export
include <lib/generated_constants.scad>
use <sgh1_skid_frame.scad>
use <sgh1_membrane_housing.scad>
use <sgh1_manifold_feed.scad>
use <sgh1_manifold_draw.scad>
use <chorus_skid_enclosure.scad>
use <chorus_aeh_panel.scad>
use <sgh1_pump_mount.scad>
use <sgh1_px_module.scad>
use <sgh1_turbine_housing.scad>
use <sgh1_drip_tray.scad>

gap = 80;
x0 = frame_L/2;
y0 = frame_W/2;

color("silver") translate([-frame_L/2, -frame_W/2, 0]) skid_frame();
color("gray") translate([20, 20, 30]) drip_tray();

color("blue") translate([x0, y0, 120]) housing_shell();
color("cyan") translate([x0, y0, 120+gap]) housing_shell();
color("green") translate([x0 - housing_len/2 - 60, y0, 120]) feed_manifold();
color("red") translate([x0 + housing_len/2 + 60, y0, 120]) draw_manifold();
color("orange") translate([x0 + housing_len/2 + 140, y0, 140]) px_module();
color("yellow") translate([x0 + housing_len/2 + 200, y0, 150]) turbine_housing();
color("white", 0.5) translate([x0, y0, 120-gap]) chorus_enclosure();
color("purple") translate([frame_L - 100, 60, 250]) rotate([0,90,0]) aeh_panel();
color("black") translate([60, y0-80, 50]) pump_mount();
