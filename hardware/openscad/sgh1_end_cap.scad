// CHORUS-SGH-1 — housing end cap (feed or draw — mirror in assembly)
include <lib/generated_constants.scad>
include <lib/utils.scad>

wall = 10;
cap_t = 18;

module end_cap(side="feed") {
    difference() {
        union() {
            cylinder(h=cap_t, d=housing_od, $fn=80);
            translate([0, 0, cap_t])
                cylinder(h=wall, d=housing_od, $fn=80);
        }
        // bore for stack
        translate([0, 0, -1])
            cylinder(h=cap_t+wall+2, d=housing_od - 2*wall, $fn=64);
        bolt_circle_pattern(8, bolt_circle/2, d=6.6, h=cap_t+wall+10);
        // port
        if (side == "feed")
            translate([housing_od/2 - wall - 5, 0, cap_t/2])
                rotate([0, 90, 0])
                    cylinder(h=wall+15, d=22, $fn=32);
        else
            translate([-housing_od/2 + wall + 5, 0, cap_t/2])
                rotate([0, -90, 0])
                    cylinder(h=wall+15, d=22, $fn=32);
    }
    // O-ring groove on face
    translate([0, 0, cap_t+wall-2])
        o_ring_groove(housing_od - 2*wall - 6);
}

end_cap("feed");
