#!/usr/bin/env python3

# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import argparse
from pathlib import Path

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform, sim_build_argdict, sim_build_args
from litex.build.sim.config import SimConfig
from litex.gen.fhdl.namer import escape_identifier_name
from litex.gen.fhdl.verilog import VerilogTime
from litex.soc.cores.uart import RS232PHYModel
from litex.soc.integration.builder import *
from litex.soc.integration.soc_core import *
from migen import *

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),
    # Serial.
    (
        "serial",
        0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data", Pins(8)),
        Subsignal("sink_valid", Pins(1)),
        Subsignal("sink_ready", Pins(1)),
        Subsignal("sink_data", Pins(8)),
    ),
]


# Platform -----------------------------------------------------------------------------------------


class Platform(SimPlatform):
    def __init__(self, sim_toolchain):
        output_dir = None
        mname = "sim"
        if sim_toolchain != "verilator":
            mname = escape_identifier_name(Path(__file__).stem)
            output_dir = os.path.join("build", mname + "_" + sim_toolchain)
        super().__init__(self, _io, name=mname, toolchain=sim_toolchain)
        self.output_dir = output_dir


# Bench SoC ----------------------------------------------------------------------------------------


class SimSoC(SoCCore):
    def __init__(self, sim_toolchain, sys_clk_freq=None, **kwargs):
        platform = Platform(sim_toolchain)
        sys_clk_freq = int(sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCMini.__init__(
            self,
            platform,
            clk_freq=sys_clk_freq,
            ident="simple_sim serial loopback",
            **kwargs,
        )

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # Serial -----------------------------------------------------------------------------------
        self.submodules.uart_phy = RS232PHYModel(platform.request("serial"))
        self.comb += self.uart_phy.source.connect(self.uart_phy.sink)

        # self.comb += Display("$display time comb: %0d", VerilogTime())
        # self.sync += Display("$display time: %0d", VerilogTime())


#
# Main ---------------------------------------------------------------------------------------------


def sim_args(parser):
    builder_args(parser)
    soc_core_args(parser)
    sim_build_args(parser)
    parser.add_argument("--debug-soc-gen", action="store_true", help="Don't run simulation")


def main():
    parser = argparse.ArgumentParser(description="LiteX Alternative Sim Test")
    sim_args(parser)
    args = parser.parse_args()

    sys_clk_freq = int(1e6)

    sim_config = SimConfig()
    sim_config.add_clocker("sys_clk", freq_hz=sys_clk_freq)
    sim_config.add_module("serial2tcp", "serial", args={"port": 2430})

    soc_kwargs = soc_core_argdict(args)
    builder_kwargs = builder_argdict(args)
    sim_build_kwargs = sim_build_argdict(args)

    soc_kwargs["sys_clk_freq"] = sys_clk_freq
    soc_kwargs["cpu_type"] = "None"
    soc_kwargs["with_uart"] = False
    soc_kwargs["ident_version"] = True

    soc = SimSoC(sim_toolchain=args.sim_toolchain, **soc_kwargs)

    builder_kwargs["csr_csv"] = "csr.csv"
    builder_kwargs["output_dir"] = soc.platform.output_dir

    if not args.debug_soc_gen:
        builder = Builder(soc, **builder_kwargs)
        for i in range(2):
            build = i == 0
            run = i == 1 and builder.compile_gateware
            builder.build(build=build, run=run, sim_config=sim_config, **sim_build_kwargs)


if __name__ == "__main__":
    main()
