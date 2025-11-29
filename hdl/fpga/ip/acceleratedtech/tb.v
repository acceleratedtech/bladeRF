`timescale 1ns / 1ps

module tb();
	reg clock = 0;
	reg enable = 1;
	
	reg reset = 0;
	reg i_stream0_v = 1;
	reg [15:0] i_stream0_i = 16'h0F00;
	
	initial begin $dumpfile("test.vcd"); $dumpvars(0,dut); end

	always #50 clock = ~clock;
	
	ble_8bit_gain dut(.clock(clock), .enable(enable), .reset(reset), .i_stream0_v(i_stream0_v), .i_stream0_i(i_stream0_i));
	
	integer i;
	initial begin
		i_stream0_i <= 16'h0F00;
		for (i = 0; i < 24; i += 1) @(posedge clock);
		i_stream0_i <= 16'h0100;
		for (i = 0; i < 24; i += 1) @(posedge clock);
		i_stream0_i <= 16'h0200;
		for (i = 0; i < 24; i += 1) @(posedge clock);
		i_stream0_i <= 16'h0E00;
		for (i = 0; i < 24; i += 1) @(posedge clock);
	end
	
	//initial $display("%x", dut.tap_c0 + dut.tap_c1 + dut.tap_c2 + dut.tap_c3 + dut.tap_c4 + dut.tap_c5 + dut.tap_c6 + dut.tap_c7 + dut.tap_c8 + dut.tap_c9 + dut.tap_c10 + dut.tap_c11 + dut.tap_c12 + dut.tap_c13 + dut.tap_c14);
	
	initial #10000 $finish;
endmodule
