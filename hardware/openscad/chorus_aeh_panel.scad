// CHORUS-AEH — acoustic harvest panel (Helmholtz resonators + piezo pocket)
include <lib/generated_constants.scad>

panel_w = frame_W * 0.6;
panel_h = 400;
panel_t = 28;
n_resonators_x = 6;
n_resonators_y = 4;
neck_d = 8;
cavity_d = 35;

module helmholtz_cell(x, y) {
  translate([x, y, 0]) {
    cylinder(h=panel_t, d=cavity_d, $fn=48);
    translate([0, 0, panel_t])
      cylinder(h=12, d=neck_d, $fn=32);
    // piezo pocket on back
    translate([0, 0, -4])
      cylinder(h=4.5, d=20, $fn=32);
  }
}

module aeh_panel() {
  difference() {
    cube([panel_w, panel_t, panel_h]);
  }
  step_x = panel_w / (n_resonators_x + 1);
  step_z = panel_h / (n_resonators_y + 1);
  for (ix = [1:n_resonators_x], iz = [1:n_resonators_y]) {
    helmholtz_cell(ix*step_x, iz*step_z);
  }
  // US transducer mount (Mode B) — feed-side assist
  translate([panel_w - 50, panel_t, panel_h/2])
    rotate([-90, 0, 0])
      cylinder(h=20, d=45, $fn=48);
  // wiring channel
  translate([10, panel_t/2, 10])
    cube([panel_w-20, 6, 12]);
}

module aeh_panel_part() { aeh_panel(); }
aeh_panel_part();
