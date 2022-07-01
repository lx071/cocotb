import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, Lock, Event

@cocotb.bfm(hdl={
    cocotb.bfm_vlog : cocotb.bfm_hdl_path(__file__, "hdl/SPI_Slave.v"),
    cocotb.bfm_sv : cocotb.bfm_hdl_path(__file__, "hdl/SPI_Slave.v"),
    })
class SpiInitiatorBfm():

    def __init__(self):
        self.busy = Lock()
        #self.is_reset = False
        #self.reset_ev = pybfms.event()
        self.recv_ev = Event()
        self.dat_width = 0
        self.rdat = 0
        pass
    
    async def send(self, dat):
        yield self.busy.acquire()
        
        self._send(dat)
        yield self.recv_ev.wait()
        self.recv_ev.clear()
        
        self.busy.release()
        
        #return self.rdat
        
    @cocotb.bfm_export(cocotb.bfm_uint32_t)
    def set_parameters(self, dat_width):
        self.dat_width = dat_width
        pass
        
    @cocotb.bfm_export(cocotb.bfm_uint32_t)
    def recv(self, rdat):
        self.rdat = rdat
        self.recv_ev.set()
        
    @cocotb.bfm_import(cocotb.bfm_uint32_t)
    def _send(self, dat):
        pass
        
    #@cocotb.bfm_export()
    #def _reset(self):
    #    self.is_reset = True
    #    self.reset_ev.set()
