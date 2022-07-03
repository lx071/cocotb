import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from spi_bfms import *
import random


class BfmTest:

    @cocotb.coroutine
    def run(self, dut):
        # <spi_bfms.spi_initiator_bfm.SpiInitiatorBfm object at 0x7f7dac40f430>
        # 从bfm管理器拿到python端的bfm对象，进行驱动
        u_bfm = cocotb.BfmMgr.find_bfm(".*u_bfm")

        # print("u_bfm=" + str(u_bfm))

        yield RisingEdge(dut.clk_r)
        # yield FallingEdge(dut.clk_r)

        # Send data out via the BFM
        # for i in range(4):
        #     data = 0xFF
        #     yield u_bfm.send_c(data)
        #     if data != u_bfm.rdat:
        #         raise cocotb.result.TestFailure("Expect 0xFF ; rdat=" + hex(u_bfm.rdat))
        #
        # yield Timer(10)

        for i in range(10):
            data = random.randint(0, 255)
            yield u_bfm.send_c(data)
            if data != u_bfm.rdat:
                print('===============', data, '!=', u_bfm.rdat, '================')
                raise cocotb.result.TestFailure("Expect " + hex(data) + " rdat=" + hex(u_bfm.rdat))


@cocotb.test()
def runtest(dut):
    test = BfmTest()
    yield test.run(dut)

