from migen import *
from migen.fhdl import verilog

STREAM_TYPE = [('v', 1), ('i', 16), ('q', 16)]

class Ble8bitGain(Module):
    def __init__(self, istrs, ostrs):
        self.sync.sys += ostrs[0].eq(istrs[0])
        self.sync.sys += ostrs[1].eq(istrs[1])

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

    verilog.convert(mod, name = "ble_8bit_gain", ios = ios, create_clock_domains=False).write("ble_8bit_gain.v")
