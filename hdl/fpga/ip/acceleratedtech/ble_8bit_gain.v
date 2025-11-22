/* Machine-generated using Migen */
module ble_8bit_gain(
	input enable,
	input i_stream0_v,
	input [15:0] i_stream0_i,
	input [15:0] i_stream0_q,
	output reg o_stream0_v,
	output reg [15:0] o_stream0_i,
	output reg [15:0] o_stream0_q,
	input i_stream1_v,
	input [15:0] i_stream1_i,
	input [15:0] i_stream1_q,
	output reg o_stream1_v,
	output reg [15:0] o_stream1_i,
	output reg [15:0] o_stream1_q,
	input clock,
	input reset
);



always @(posedge clock) begin
	o_stream0_v <= i_stream0_v;
	o_stream0_i <= i_stream0_i;
	o_stream0_q <= i_stream0_q;
	o_stream1_v <= i_stream1_v;
	o_stream1_i <= i_stream1_i;
	o_stream1_q <= i_stream1_q;
	if (reset) begin
		o_stream0_v <= 1'd0;
		o_stream0_i <= 16'd0;
		o_stream0_q <= 16'd0;
		o_stream1_v <= 1'd0;
		o_stream1_i <= 16'd0;
		o_stream1_q <= 16'd0;
	end
end

endmodule
