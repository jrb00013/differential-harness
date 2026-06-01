// CHORUS-SGH-1 — single membrane plate with feed spacer channels
include <lib/generated_constants.scad>
include <lib/utils.scad>

plate_t = 6;
channel_w = 2;
channel_gap = 1.5;
margin = 15;

module feed_spacer_pattern() {
    n_x = floor((active_w - 2*margin) / (channel_w + channel_gap));
    n_y = floor((active_h - 2*margin) / (channel_w + channel_gap));
    for (ix = [0:n_x-1], iy = [0:n_y-1]) {
        x = -active_w/2 + margin + ix*(channel_w+channel_gap) + channel_w/2;
        y = -active_h/2 + margin + iy*(channel_w+channel_gap) + channel_w/2;
        translate([x, y, 0])
            cube([channel_w, channel_w, plate_t], center=true);
    }
}

module membrane_plate() {
    difference() {
        plate_frame(active_w, active_h, plate_t);
        // membrane window (thin active region representation)
        translate([0, 0, plate_t/2 + 0.1])
            cube([active_w - 2*margin, active_h - 2*margin, plate_t], center=true);
    }
    feed_spacer_pattern();
    // alignment pin holes
    for (dx = [-1, 1], dy = [-1, 1])
        translate([dx*(active_w/2-8), dy*(active_h/2-8), 0])
            cylinder(h=plate_t, d=4, $fn=20);
}

membrane_plate();
