import cocotb
from spi_bfms import *



    async def test():
        
        u_bfm = cocotb.BfmMgr.find_bfm(".*u_bfm")
        print("u_bfm=" + str(u_bfm))
    
        yield cocotb.triggers.Timer(50, "ns")

        for i in range(4):
            yield u_bfm.send(0xFF)
            if u_bfm.rdat != 0xFF:
                raise cocotb.result.TestFailure("Expect 0xFF ; rdat=" + hex(rdat))

        for i in range(100):    
            yield u_bfm.send(i+1)
            if u_bfm.rdat != (i+1):
                raise cocotb.result.TestFailure("Expect " + hex(i+1) + " ; rdat=" + hex(rdat))
            

@cocotb.test()
def runtest(dut):
    
    yield test()
