###############################################################################
# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
###############################################################################

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

VERILOG_SOURCES += $(COCOTB)/tests/designs/spi_bfm/spi_initiator_smoke_tb.sv
# VERILOG_SOURCES += $(COCOTB)/tests/test_cases/test_spi_bfm/spi_bfms/hdl/spi_initiator_bfm.v
TOPLEVEL = spi_initiator_smoke_tb

MODULE = bfm_test

include $(COCOTB)/makefiles/Makefile.inc
include $(COCOTB)/makefiles/Makefile.sim

endif
