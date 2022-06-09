TOPLEVEL_LANG ?= verilog
COCOTB_BFM_MODULES += spi_bfms

ifneq ($(TOPLEVEL_LANG),verilog)

all:
	@echo "Skipping test due to TOPLEVEL_LANG=$(TOPLEVEL_LANG) not being verilog"
clean::

else

ifeq ($(OS),Msys)
WPWD=$(shell sh -c 'pwd -W')
else
WPWD=$(shell pwd)
endif

COCOTB?=$(WPWD)/../../..

VERILOG_SOURCES = spi_initiator_smoke_tb.sv
TOPLEVEL = spi_initiator_smoke_tb

MODULE = bfm_test

include $(COCOTB)/makefiles/Makefile.inc
include $(COCOTB)/makefiles/Makefile.sim

endif
