// CHORUS-SGH-1 — 8020-style skid frame (aluminum extrusion representation)
include <lib/generated_constants.scad>

profile = 40;
wall_t = 3;

module extrusion_bar(len, axis="x") {
    if (axis == "x")
        cube([len, profile, profile]);
    else if (axis == "y")
        cube([profile, len, profile]);
    else
        cube([profile, profile, len]);
}

module skid_frame() {
    L = frame_L;
    W = frame_W;
    H = frame_H;
    // corners vertical
    for (dx = [0, L-profile], dy = [0, W-profile]) {
        translate([dx, dy, 0])
            extrusion_bar(H, "z");
    }
    // lower horizontal
    for (z = [0, H-profile]) {
        translate([0, 0, z]) {
            extrusion_bar(L, "x");
            translate([0, W-profile, 0])
                extrusion_bar(L, "x");
            extrusion_bar(W, "y");
            translate([L-profile, 0, 0])
                extrusion_bar(W, "y");
        }
    }
    // drip tray lip
    translate([20, 20, 20])
        difference() {
            cube([L-40, W-40, 5]);
            translate([5, 5, -1])
                cube([L-50, W-50, 7]);
        }
    // mounting feet
    for (dx = [30, L-50], dy = [30, W-50]) {
        translate([dx, dy, -8])
            cylinder(h=8, d=50, $fn=48);
    }
}

module sgh1_skid_frame_part() { skid_frame(); }
sgh1_skid_frame_part();
