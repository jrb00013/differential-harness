// Shared utilities for CHORUS-SGH-1 OpenSCAD

module flanged_port(od=16, length=25, flange_od=40, flange_t=6) {
    translate([0, 0, -length])
        cylinder(h=length, d=od, $fn=32);
    cylinder(h=flange_t, d=flange_od, $fn=48);
}

module o_ring_groove(dia, depth=2.2, width=3.0) {
    rotate_extrude($fn=64)
        translate([dia/2 - depth, 0])
            square([depth, width], center=true);
}

module bolt_hole(d=6.6, h=50) {
    cylinder(h=h, d=d, $fn=24);
}

module bolt_circle_pattern(n, radius, d=6.6, h=50) {
    for (i = [0:n-1]) {
        ang = 360 * i / n;
        rotate([0, 0, ang])
            translate([radius, 0, 0])
                bolt_hole(d=d, h=h);
    }
}

module plate_frame(w, h, t, corner_r=8) {
    linear_extrude(t)
        offset(r=corner_r)
            square([w - 2*corner_r, h - 2*corner_r], center=true);
}
