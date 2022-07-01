#!/usr/bin/env python3

#!/usr/bin/env python3

# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import argparse
from pathlib import Path

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.gen.fhdl.namer import escape_identifier_name
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
        if sim_toolchain == "verilator":
            mname = "sim"
        else:
            mname = escape_identifier_name(Path(__file__).stem)
        super().__init__(self, _io, name=mname, toolchain=sim_toolchain)


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


#
# Main ---------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="LiteX Alternative Sim Test")
    parser.add_argument("--debug-soc-gen", action="store_true", help="Don't run simulation")
    parser.add_argument("--sim-toolchain", default="verilator", help="Simulation toolchain")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    sys_clk_freq = int(1e6)

    sim_config = SimConfig()
    sim_config.add_clocker("sys_clk", freq_hz=sys_clk_freq)
    sim_config.add_module("serial2tcp", "serial", args={"port": 2430})

    soc_kwargs = soc_core_argdict(args)
    builder_kwargs = builder_argdict(args)

    soc_kwargs["sys_clk_freq"] = sys_clk_freq
    soc_kwargs["cpu_type"] = "None"
    soc_kwargs["with_uart"] = False
    soc_kwargs["ident_version"] = True

    builder_kwargs["csr_csv"] = "csr.csv"

    soc = SimSoC(sim_toolchain=args.sim_toolchain, **soc_kwargs)
    if not args.debug_soc_gen:
        builder = Builder(soc, **builder_kwargs)
        for i in range(2):
            build = i == 0
            run = i == 1 and builder.compile_gateware
            builder.build(
                build=build,
                run=run,
                sim_config=sim_config,
            )


if __name__ == "__main__":
    main()
