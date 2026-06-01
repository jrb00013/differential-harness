// CHORUS-SGH-1 — low-salinity feed manifold
include <lib/generated_constants.scad>
include <lib/utils.scad>

module feed_manifold() {
    body_l = 120;
    body_w = active_w + 40;
    body_h = 50;
    difference() {
        translate([-body_l/2, -body_w/2, 0])
            cube([body_l, body_w, body_h]);
        // internal plenum
        translate([-body_l/2 + 8, -body_w/2 + 8, 8])
            cube([body_l-16, body_w-16, body_h]);
        // outlet to housing
        translate([body_l/2 - 5, 0, body_h/2])
            rotate([0, 90, 0])
                cylinder(h=30, d=22, $fn=40);
        // inlet (NPT representation)
        translate([-body_l/2 + 15, 0, body_h])
            cylinder(h=25, d=28, $fn=40);
        // conductivity sensor port
        translate([0, body_w/2 - 10, body_h/2])
            rotate([90, 0, 0])
                cylinder(h=20, d=12, $fn=24);
        // mounting
        for (x = [-body_l/2+15, body_l/2-15])
            translate([x, -body_w/2+12, -1])
                bolt_hole(d=6.6, h=body_h+10);
    }
}

module sgh1_manifold_feed_part() { feed_manifold(); }
sgh1_manifold_feed_part();
