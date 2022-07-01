# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
print('==============import cocotb================')
import cocotb
print('==============import Timer================')
from cocotb.triggers import Timer
print('==============import rv_bfms================')
from rv_bfms import *
print('==============import finished================')

class BfmTest(ReadyValidDataMonitorIF):

    def __init__(self):
        self.data_l = []

    def data_recv(self, d):
        self.data_l.append(d)

    @cocotb.coroutine
    def run(self):
        bfm = cocotb.BfmMgr.find_bfm(".*u_dut")
        mon = cocotb.BfmMgr.find_bfm(".*u_mon")

        mon.add_listener(self)

        # Send data out via the BFM
        for i in range(100):
            yield bfm.write_c(i)

        yield Timer(10)

        if len(self.data_l) != 100:
            raise TestError("len (%d) != 100" % len(self.data_l))

@cocotb.test()
def runtest(dut):
    # print('========test create======')
    test = BfmTest()
    # print('========test run======')
    yield test.run()
    # print('========test end======')


