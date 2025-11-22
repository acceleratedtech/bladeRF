module ble_8bit_gain(
  input clock,
  input reset,
  input enable,
  input        i_stream0_v,
  input [15:0] i_stream0_i,
  input [15:0] i_stream0_q,
  input        i_stream1_v,
  input [15:0] i_stream1_i,
  input [15:0] i_stream1_q,
  output        o_stream0_v,
  output [15:0] o_stream0_i,
  output [15:0] o_stream0_q,
  output        o_stream1_v,
  output [15:0] o_stream1_i,
  output [15:0] o_stream1_q
);

  assign o_stream0_v = i_stream0_v;
  assign o_stream0_i = i_stream0_i;
  assign o_stream0_q = i_stream0_q;
  assign o_stream1_v = i_stream1_v;
  assign o_stream1_i = i_stream1_i;
  assign o_stream1_q = i_stream1_q;

endmodule
