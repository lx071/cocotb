import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, Lock, Event
print('=================cocotb.bfm================')


# 如果当前文件包含在sys.path里面,那么,__file__返回一个相对路径! 如果当前文件不包含在sys.path里面,那么__file__返回一个绝对路径
# verilog-bfm路径
@cocotb.bfm(hdl={
    cocotb.bfm_vlog: cocotb.bfm_hdl_path(__file__, "hdl/spi_initiator_bfm.v"),
    cocotb.bfm_sv: cocotb.bfm_hdl_path(__file__, "hdl/spi_initiator_bfm.v"),
    })
class SpiInitiatorBfm:

    def __init__(self):
        self.busy = Lock()
        #self.is_reset = False
        #self.reset_ev = pybfms.event()
        self.recv_ev = Event()
        self.dat_width = 0
        self.rdat = 0
        
    @cocotb.coroutine
    def send_c(self, dat):
        yield self.busy.acquire()
        
        self.send(dat)
        yield self.recv_ev.wait()
        self.recv_ev.clear()
        
        self.busy.release()

    # 由SV层进行调用
    @cocotb.bfm_export(cocotb.bfm_uint32_t)
    def recv(self, rdat):
        self.rdat = rdat
        self.recv_ev.set()

    # 调用SV层的task
    @cocotb.bfm_import(cocotb.bfm_uint32_t)
    def send(self, dat):
        pass
        
    #@cocotb.bfm_export()
    #def _reset(self):
    #    self.is_reset = True
    #    self.reset_ev.set()
