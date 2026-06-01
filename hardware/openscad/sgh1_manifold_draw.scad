// CHORUS-SGH-1 — high-salinity draw / brine manifold (rated for ΔP*)
include <lib/generated_constants.scad>
include <lib/utils.scad>

module draw_manifold() {
    body_l = 140;
    body_w = active_w + 40;
    body_h = 60;
    difference() {
        translate([-body_l/2, -body_w/2, 0])
            cube([body_l, body_w, body_h]);
        translate([-body_l/2 + 10, -body_w/2 + 10, 10])
            cube([body_l-20, body_w-20, body_h]);
        translate([-body_l/2 + 5, 0, body_h/2])
            rotate([0, -90, 0])
                cylinder(h=30, d=22, $fn=40);
        // brine return
        translate([body_l/2 - 20, body_w/4, body_h])
            cylinder(h=30, d=24, $fn=40);
        // PX / turbine outlet (pressurized draw)
        translate([body_l/2 - 20, -body_w/4, body_h])
            cylinder(h=35, d=32, $fn=40);
        // pressure transducer port
        translate([0, -body_w/2 + 12, body_h - 8])
            rotate([-90, 0, 0])
                cylinder(h=15, d=10, $fn=20);
        for (x = [-body_l/2+18, body_l/2-18])
            translate([x, body_w/2-12, -1])
                bolt_hole(d=8.6, h=body_h+12);
    }
    // label boss (emboss in print)
    translate([0, 0, body_h])
        linear_extrude(1)
            text(str("DP~", delta_P_bar, "bar"), size=6, halign="center");
}

module sgh1_manifold_draw_part() { draw_manifold(); }
sgh1_manifold_draw_part();
