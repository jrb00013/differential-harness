// CHORUS-SGH-1 — membrane stack housing (cylinder shell + plate slots)
include <lib/generated_constants.scad>
include <lib/utils.scad>

wall = 10;

module housing_shell() {
    stack_len = n_plates * plate_pitch + 40;
    difference() {
        cylinder(h=stack_len, d=housing_od, $fn=80);
        translate([0, 0, wall])
            cylinder(h=stack_len, d=housing_od - 2*wall, $fn=64);
        // sight / sensor slot
        translate([housing_od/2 - wall/2, -15, stack_len/2])
            cube([wall+2, 30, 60], center=true);
    }
    // plate guide rails
    for (z = [20:plate_pitch:n_plates*plate_pitch+15]) {
        translate([0, (housing_od/2 - wall - 3), z])
            cube([housing_od - 2*wall, 3, 2], center=true);
        translate([0, -(housing_od/2 - wall - 3), z])
            cube([housing_od - 2*wall, 3, 2], center=true);
    }
}

module sgh1_membrane_housing_part() { housing_shell(); }
sgh1_membrane_housing_part();
