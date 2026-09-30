`timescale 1ns/1ps

module tb_CPUtop;

    reg clk = 0;
    reg rst = 1;
    reg [17:0] instruction_in = 0;
    reg [15:0] data_in = 0;
    wire [15:0] data_out;
    wire [9:0] instruction_address;
    wire [9:0] data_address;
    wire data_R, data_W, done;

    CPUtop dut (
        .clk(clk),
        .rst(rst),
        .instruction_in(instruction_in),
        .data_in(data_in),
        .data_out(data_out),
        .instruction_address(instruction_address),
        .data_address(data_address),
        .data_R(data_R),
        .data_W(data_W),
        .done(done)
    );

    // clock: 10ns period
    always #5 clk = ~clk;

    initial begin
        $dumpfile("cputop.vcd");
        $dumpvars(0, tb_CPUtop);

        rst = 1;
        #20;
        rst = 0;

        // Example instruction (edit opcode/fields per your ISA)
        instruction_in = 18'b000000_0000000000_00;
        #40;

        // add more instructions here as needed
        instruction_in = 18'b000001_0000000001_00;
        #40;

        #200;
        $finish;
    end

endmodule
