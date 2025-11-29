import math

from migen import *
from litex.gen.fhdl import verilog

from litex.gen import LiteXModule

class FirGain(LiteXModule):
    TAPS_HEAVY = [
        -0.02916985,
        0.07374786,
        -0.22707693,
        0.57625092,
        -1.2575477,
        2.41501576,
        -3.8305809,
        5.53418559, 
        -3.8305809,
        2.41501576,
        -1.2575477,
        0.57625092,
        -0.22707693,
        0.07374786,
        -0.02916985,
        # this is symmetric so we can replace some multiplication with some
        # DFFs, but that optimization can come later
    ]
    
    TAPS_LIGHT = [ 0.01281782, -0.01885119,  0.01903052,  0.03090074, -0.24487562,
        0.81767817, -1.71217123,  3.20280773, -1.71217123,  0.81767817,
       -0.24487562,  0.03090074,  0.01903052, -0.01885119,  0.01281782]
    
    TAPS = TAPS_LIGHT
    
    # signed, SN.M format
    TAP_N = 3  # bits before decimal
    TAP_M = 12 # bits after decimal
    
    INP_BITS = 12 # S0.12
    OUP_BITS = 1+TAP_N+16 # S3.16
    FINAL_BITS = 1+TAP_N+12 # S3.12
    PIPE_STAGES = 5
    
    def __init__(self, d, ce):
        taps_int = [ math.trunc(tap * 2**self.TAP_M) for tap in self.TAPS ]
        taps_int = [ ((2 ** (1 + self.TAP_N + self.TAP_M)) + tap) if tap < 0 else tap for tap in taps_int ]
        
        d_delay = Signal((self.INP_BITS, True))
        self.comb += d_delay.eq(d)
        qs = []
        
        for tap in taps_int:
            ndelay = Signal((self.INP_BITS, True))
            tap_c = Signal((1 + self.TAP_N + self.TAP_M, True), reset=tap)
            
            self.sync += If(ce, ndelay.eq(d_delay))
            
            mul_q = Signal((self.OUP_BITS, True))
            mul_int = Signal((1 + self.TAP_N + self.TAP_M + self.INP_BITS, True))
            self.comb += mul_int.eq(d_delay * tap_c)
            self.sync += If(ce, mul_q.eq(mul_int[-self.OUP_BITS:]))
            qs.append(mul_q)
            
            d_delay = ndelay
        
        q_sum = sum([Cat(x, Constant(0)) for x in qs])
        for _ in range(self.PIPE_STAGES):
            nq_sum = Signal((self.OUP_BITS, True))
            self.sync += If(ce, nq_sum.eq(q_sum))
            q_sum = nq_sum
        
        q_trim = q_sum[-self.FINAL_BITS-1:]

        # round nearest
        q_round = Signal(self.FINAL_BITS)
        self.sync += If(ce, q_round.eq(q_trim[1:] + q_trim[0]))
        
        # and this is DEFINITELY not symbolically correct!
        self.q = Mux((q_round[-1] != q_round[-2]) | (q_round[-1] != q_round[-3]) | (q_round[-1] != q_round[-4]) | (q_round[-1] != q_round[-5]),
                     Mux(q_round[-1], 0x800, 0x7FF),
                     q_round[:self.INP_BITS])



STREAM_TYPE = [('v', 1), ('i', 16), ('q', 16)]

class Ble8bitGain(LiteXModule):
    def __init__(self, istrs, ostrs):
        self.firgain_0i = FirGain(istrs[0].i[0:12], istrs[0].v)
        self.firgain_0q = FirGain(istrs[0].q[0:12], istrs[0].v)
        
        #q_ctr = Signal(16)
        #self.sync += If(istrs[0].v, q_ctr.eq(q_ctr + 1))
        #self.submodules += firgain_0q
    
        self.comb += ostrs[0].v.eq(istrs[0].v)
        self.comb += ostrs[0].i.eq(self.firgain_0i.q)
        #self.comb += ostrs[0].q.eq(q_ctr)
        self.comb += ostrs[0].q.eq(self.firgain_0q.q)
        
        self.sync += ostrs[1].eq(istrs[1])

if __name__ == '__main__':
    enable = Signal(1)
    enable.name_override = "enable"

    i_stream0 = Record(STREAM_TYPE)
    i_stream0.v.name_override = "i_stream0_v"
    i_stream0.i.name_override = "i_stream0_i"
    i_stream0.q.name_override = "i_stream0_q"
    o_stream0 = Record(STREAM_TYPE)
    o_stream0.v.name_override = "o_stream0_v"
    o_stream0.i.name_override = "o_stream0_i"
    o_stream0.q.name_override = "o_stream0_q"
    i_stream1 = Record(STREAM_TYPE)
    i_stream1.v.name_override = "i_stream1_v"
    i_stream1.i.name_override = "i_stream1_i"
    i_stream1.q.name_override = "i_stream1_q"
    o_stream1 = Record(STREAM_TYPE)
    o_stream1.v.name_override = "o_stream1_v"
    o_stream1.i.name_override = "o_stream1_i"
    o_stream1.q.name_override = "o_stream1_q"
    
    ios = set()
    ios.add(enable)
    ios.add(i_stream0.v)
    ios.add(i_stream0.i)
    ios.add(i_stream0.q)
    ios.add(o_stream0.v)
    ios.add(o_stream0.i)
    ios.add(o_stream0.q)
    ios.add(i_stream1.v)
    ios.add(i_stream1.i)
    ios.add(i_stream1.q)
    ios.add(o_stream1.v)
    ios.add(o_stream1.i)
    ios.add(o_stream1.q)
    
    mod = Ble8bitGain( [i_stream0, i_stream1], [o_stream0, o_stream1] )
    mod.clock_domains.sys = cd_sys = ClockDomain("sys")
    cd_sys.clk.name_override = 'clock'
    cd_sys.rst.name_override = 'reset'
    ios.add(cd_sys.clk)
    ios.add(cd_sys.rst)

    verilog.convert(mod, name = "ble_8bit_gain", ios = ios).write("ble_8bit_gain.v")
