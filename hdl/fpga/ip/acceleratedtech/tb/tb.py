import os, sys
import shutil
from pathlib import Path
from dataclasses import dataclass

import cocotb
from cocotb_tools.runner import get_runner

@dataclass
class TestConfig:
    verilog_sources : list[str] = None
    toplevel : str = None
    path : str = ""
    defines : dict[str, str] = None
    
    def build(self):
        pass

def tb_main(config, modname = None, waves = True):
    if not modname:
        file = sys.modules['__main__'].__file__
        modname = os.path.splitext(os.path.basename(file))[0]
    
    config.build()
    
    root_path = Path(__file__).resolve().parent.parent
    simtype = os.getenv("SIM", "icarus") # or 'verilator'
    simargs = []
    if simtype == "verilator":
        simargs = ["-Wno-fatal", "-CFLAGS", "-O2"]
    runner = get_runner(simtype)
    
    runner.build(verilog_sources = [ root_path / f for f in config.verilog_sources],
                 hdl_toplevel = config.toplevel,
                 defines = config.defines or {},
                 always = True,
                 waves = waves,
                 build_dir = root_path / config.path / "tb_build",
                 build_args = simargs)
    
    if len(sys.argv) >= 2:
        for testcase in sys.argv[1:]:
            runner.test(hdl_toplevel = config.toplevel, test_module=modname, waves=waves, test_dir=root_path / config.path, testcase=testcase)
    else:
        runner.test(hdl_toplevel = config.toplevel, test_module=modname, waves=waves, test_dir=root_path / config.path)
