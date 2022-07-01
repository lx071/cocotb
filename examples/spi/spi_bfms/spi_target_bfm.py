import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, Lock, Event

@cocotb.bfm(hdl={
    cocotb.bfm_vlog : cocotb.bfm_hdl_path(__file__, "hdl/spi_target_bfm.v"),
    cocotb.bfm_sv :  : cocotb.bfm_hdl_path(__file__, "hdl/spi_target_bfm.v"),
    }, has_init=True)
class SpiTargetBfm():

    def __init__(self):
        self.busy = Lock()
        self.is_reset = False
        self.reset_ev = Event()
        self.recv_start_f = None
        self.recv_f = None
        self.clocked_csn_high_f = None
        pass

    def send(self, data):
        self._send(data)
        
    @cocotb.bfm_export()
    def _recv_start(self):
        if self.recv_start_f is not None:
            data = self.recv_start_f()
            self._send(data)

    @cocotb.bfm_export(cocotb.bfm_uint64_t)    
    def _recv(self, data):
        if self.recv_f is not None:
            self.recv_f(data)
        else:
            print("Note: received data " + hex(data))
            
    @cocotb.bfm_export()
    def _clocked_csn_high(self):
        print("clocked_csn_high")
        if self.clocked_csn_high_f is not None:
            self.clocked_csn_high_f()
        pass
            
    @cocotb.bfm_import(cocotb.bfm_uint64_t)
    def _send(self, data):
        pass
        
    @cocotb.bfm_export(cocotb.bfm_uint32_t)
    def _set_parameters(self, dat_width):
        self.dat_width = dat_width
        pass
        
    @cocotb.bfm_export()
    def _reset(self):
        self.is_reset = True
        self.reset_ev.set()
