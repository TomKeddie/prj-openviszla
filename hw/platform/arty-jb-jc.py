from ovplatform.ov3 import Platform
from ovhw.top import OV3
from migen.build.generic_platform import *
from migen.build.xilinx import XilinxPlatform
from migen.genlib.io import CRG

_io = [
    ("leds", 0, Pins("H5 J5 T9"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),

    ("btn", 0, Pins("D9"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),
#    Spare 50MHz clock for bringup
#    ("clk50", 0, Pins("P94"), IOStandard("LVCMOS33")),
#    FT2232H clock    
#    ("clk12", 0, Pins("P50"), IOStandard("LVCMOS33")),

    ("ulpi", 0, 
        Subsignal("d", Pins("P120 P119 P118 P117 P116 P115 P114 P112")),
        Subsignal("rst", Pins("P127")),
        Subsignal("stp", Pins("P126")),
        Subsignal("dir", Pins("P124")),
        Subsignal("clk", Pins("P123"), Misc("PULLDOWN")),
        Subsignal("nxt", Pins("P121")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),

#    ("ftdi", 0,
#        Subsignal("clk", Pins("P51")),
#        Subsignal("d", Pins("P65 P62 P61 P46 P45 P44 P43 P48")),
#        Subsignal("rxf_n", Pins("P55")),
#        Subsignal("txe_n", Pins("P70")),
#        Subsignal("rd_n", Pins("P41")),
#        Subsignal("wr_n", Pins("P40")),
#        Subsignal("siwua_n", Pins("P66")),
#        Subsignal("oe_n", Pins("P38")),
#        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
#    ),

#    ("sdram", 0,
#        Subsignal("clk", Pins("P24")),
#        Subsignal("a", Pins("P7 P8 P9 P10 P35 P34 P33 P32 P30 P29 P6 P27 P26")),
#        Subsignal("ba", Pins("P2 P5")),
#        Subsignal("cs_n", Pins("P1")),
#        Subsignal("cke", Pins("P56")),
#        Subsignal("ras_n", Pins("P144")),
#        Subsignal("cas_n", Pins("P143")),
#        Subsignal("we_n", Pins("P142")),
#        Subsignal("dq", Pins("P131 P132 P133 P134 P137 P138 P139 P140 "
#                             "P22 P21 P17 P16 P15 P14 P12 P11")),
#        Subsignal("dqm", Pins("P141 P23")),
#        IOStandard("LVCMOS33"), Drive(8), Misc("SLEW=FAST")
#    ),

]

class Platform(XilinxPlatform):
    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a35t-csg324-1", _io, toolchain="vivado")


    def do_finalize(self, fragment):
        # Add the CRG
        crg = CRG(self.request("clk50"))
        fragment += crg.get_fragment()

        clocks = {
            "clk50": 50.0,
            "clk12": 12.0,
            ("ulpi", "clk"): 60.0,
            ("ftdi", "clk"): 60.0
        }

        # Make sure init_b is used / added to the UCF
        self.request("init_b")

        for name, mhz in clocks.items():
            period = 1000.0 / mhz
            try:
                if isinstance(name, tuple):
                    clk = getattr(self.lookup_request(name[0]), name[1])
                else:
                    clk = self.lookup_request(name)
                self.add_platform_command("""
NET "{clk}" TNM_NET = "GRP{clk}";
TIMESPEC "TS{clk}" = PERIOD "GRP{clk}" %f ns HIGH 50%%;
""" % period, clk=clk)
            except ConstraintError:
                pass
if __name__ == "__main__":
    plat = Platform()
    top = OV3(plat)
