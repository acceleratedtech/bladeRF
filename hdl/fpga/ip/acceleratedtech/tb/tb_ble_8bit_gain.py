import logging
import math
from queue import deque

import cocotb
from cocotb.clock import Clock, Timer, RisingEdge

try:
    import ble_8bit_gain
except:
    pass # it'll be ok during simulation

from tb import *

TEST_CONFIG = TestConfig(
    verilog_sources = ["ble_8bit_gain.v"],
    toplevel = "ble_8bit_gain"
)

async def do_clock_and_reset(dut):
    cocotb.start_soon(Clock(dut.clock, 10,"ns").start()) # 100MHz
    dut.reset.value = 0
    await Timer(1, "us")
    dut.reset.value = 1
    await Timer(1, "us")
    dut.reset.value = 0
    dut.enable.value = 1
    await RisingEdge(dut.clock)

def s12_to_f32(s12):
    f32 = float(s12) / (2 ** 11)
    if f32 >= 1:
        f32 = -2 + f32
    return f32

def f32_to_s12(f32):
    s12 = math.trunc(f32 * 2**11)
    assert(s12 >= -2048 and s12 <= 2047)
    if s12 < 0:
        s12 += 2 ** 12
    return s12

assert(s12_to_f32(0x0400) == 0.5)
assert(s12_to_f32(0x0800) == -1)
assert(s12_to_f32(f32_to_s12(0.25)) == 0.25)
assert(s12_to_f32(f32_to_s12(-0.25)) == -0.25)

async def xchg_sample(dut, samp16):
    dut.i_stream0_v.value = 1
    dut.i_stream0_i.value = samp16
    dut.i_stream0_q.value = 0
    await RisingEdge(dut.clock)
    assert(dut.o_stream0_v.value == 1)
    return dut.i_stream0_i.value

async def xchg_sample_f32(dut, samp):
    return s12_to_f32(await xchg_sample(dut, f32_to_s12(samp)))

class FirChecker:
    def __init__(self, clk, d, q, taps, latency = 7):
        self.clk = clk
        self.d = d
        self.q = q
        self.taps = taps
        self.latency = latency
        self.logger = logging.getLogger(f"cocotb.{q._path}")
        self.failures = 0
        self.cycles = 0
        self.failures_max = 20
        self.tolerance = 2 / (2 ** 11)
    
    async def run(self):
        d_buf = deque([ 0.0 for _ in self.taps ])
        latency_buf = deque([ 0.0 for _ in range(self.latency) ])
        while True:
            await RisingEdge(self.clk)
            d_buf.rotate(-1)
            d_buf[-1] = s12_to_f32(self.d.value)
        
            # do the actual dot product
            q_out = sum(k * d for k, d in zip(self.taps, d_buf))
        
            latency_buf.rotate(-1)
            latency_buf[-1] = q_out
            
            # now check Q for realsies
            q_delay = latency_buf[0]
            q_f32 = s12_to_f32(self.q.value)
            
            delta = abs(q_f32 - q_delay)
            
            if delta > self.tolerance:
                self.failures += 1
                self.logger.error(f"clk {self.cycles}: failure {self.failures}: anticipated {q_delay} (0x{f32_to_s12(q_delay):04x}), got {q_f32} (0x{int(self.q.value):04x})")
            else:
                self.logger.info(f"clk {self.cycles}: failure {self.failures}: anticipated {q_delay} (0x{f32_to_s12(q_delay):04x}), got {q_f32} (0x{int(self.q.value):04x})")
            
            self.cycles += 1

@cocotb.test()
async def test_dc_equiv(dut):
    await do_clock_and_reset(dut)
    
    checker = FirChecker(dut.clock, dut.i_stream0_i, dut.o_stream0_i, ble_8bit_gain.FirGain.TAPS)
    cocotb.start_soon(checker.run())

    for _ in range(16):
        await xchg_sample_f32(dut, 0)
    
    for _ in range(24):
        await xchg_sample_f32(dut, 0.4)
    
    if checker.failures:
        raise AssertionError("too many mismatches")

if __name__ == "__main__":
    tb_main(TEST_CONFIG)
