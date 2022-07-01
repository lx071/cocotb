
module spi_initiator_smoke_tb;
	

	reg clk_r = 0;
	//reg clock = 0;
	always #10 clk_r <= ~clk_r;
	
	wire sck;
	wire sdo;
	wire sdi;
	wire[3:0] csn;

	// Simple loopback
	assign sdi = sdo;

	spi_initiator_bfm u_bfm(
			.clk(clk_r),
			.sck(				sck),
			.sdo(				sdo),
			.sdi(				sdi),
			.csn(				csn)
			);
	`ifdef __ICARUS__
	initial begin
  		$dumpfile("waveform.vcd");
  		$dumpvars;
	end
	`endif
endmodule
