# ---------------------------------------------------------------
# CPUtop.sdc — timing constraints for OpenLane2 / Sky130
# Conservative first-pass constraints. Tighten CLOCK_PERIOD once
# you have a clean STA report with margin.
# ---------------------------------------------------------------

# Clock: 50 ns period (20 MHz) — generous starting point for a
# 5-stage FSM CPU with no deep combinational paths (16-bit SIMD
# adder/multiplier tree is the longest path, still small).
create_clock [get_ports clk] -name clk -period 50

# Input/output delay budget: 20% of the clock period reserved
# for off-chip / testbench interfacing margin.
set_input_delay  -clock clk 5 [all_inputs -no_clocks]
set_output_delay -clock clk 5 [all_outputs]

# rst is a synchronous reset muxed into the D-input logic (not
# tied to flop SET/RESET pins), so no special async reset
# handling or false-path is required.
