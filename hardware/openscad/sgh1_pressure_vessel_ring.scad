// CHORUS-SGH-1 — reinforcing ring for pressurized draw side
include <lib/generated_constants.scad>

module pressure_ring() {
    difference() {
        cylinder(h=15, d=housing_od - 20, $fn=72);
        cylinder(h=16, d=housing_od - 45, $fn=64);
    }
}

pressure_ring();
