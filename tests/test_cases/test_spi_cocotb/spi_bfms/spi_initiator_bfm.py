import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, Lock, Event
print('=================cocotb.bfm================')
@cocotb.bfm(hdl={
    cocotb.bfm_vlog : cocotb.bfm_hdl_path(__file__, "hdl/spi_initiator_bfm.v"),
    cocotb.bfm_sv : cocotb.bfm_hdl_path(__file__, "hdl/spi_initiator_bfm.v"),
    })
class SpiInitiatorBfm():

    def __init__(self):
        self.busy = Lock()
        #self.is_reset = False
        #self.reset_ev = pybfms.event()
        self.recv_ev = Event()
        self.dat_width = 0
        self.rdat = 0
        
    @cocotb.coroutine
    def send_c(self, dat, dut):
        yield self.busy.acquire()

        dut.u_bfm.xmit_en = 1
        dut.u_bfm.dat_out_v = dat
        # self.send(dat)
        yield self.recv_ev.wait()
        self.recv_ev.clear()
        
        self.busy.release()

    @cocotb.bfm_export(cocotb.bfm_uint32_t)
    def recv(self, rdat):
        self.rdat = rdat
        self.recv_ev.set()
        
    @cocotb.bfm_import(cocotb.bfm_uint32_t)
    def send(self, dat):
        pass
        
    #@cocotb.bfm_export()
    #def _reset(self):
    #    self.is_reset = True
    #    self.reset_ev.set()
