module spi_initiator_smoke_tb;


	reg clk_r = 0;
	//reg clock = 0;
	always #10 clk_r <= ~clk_r;

	wire sck;
	wire sdo;
	wire sdi;
	wire[3:0] csn;
	wire sel;

    //`define task_send u_bfm.send

	assign sel = csn[0];
	spi_initiator_bfm u_bfm(
			.clk(clk_r),
			.sck(				sck),
			.sdo(				sdo),
			.sdi(				sdi),
			.csn(				csn)
			);

	SPI_Slave target(
			.clk(clk_r),
			.SCK(sck),
			.SSEL(sel),
			.MOSI(sdo),
			.MISO(sdi)
	);
	reg[7:0] data;

    reg[7:0] data_recv;
    initial begin
        //$display("$time=%0t",$realtime);
        //$display("$time=%0t",$time);
        repeat(100000) begin
            data = $urandom_range(0,255);
            u_bfm.send(data);
            repeat(8) @(posedge clk_r);
            //$display("data:%d , data_recv:%d", data, data_recv);

            while (data!=data_recv) begin
                repeat(8) @(posedge clk_r);
                u_bfm.recv(data_recv);
                //$display("%d != %d", data, data_recv);
            end

            //$display("data:%d , data_recv:%d", data, data_recv);
            //$display(data_recv);
        end
        //$display("$time=%0t",$realtime);
        //$display("$time=%0t",$time);
        $stop;
    end


	`ifdef __ICARUS__
	initial begin
  	    $dumpfile("waveform.vcd");
  	    $dumpvars;
	end
	`endif
endmodule

module SPI_Slave(
                 clk,
                 SCK, SSEL, MOSI,MISO//SPI communication pin

                 );
 input clk;
 input SCK, SSEL, MOSI;
 output MISO;

 reg [7:0] mem;

 assign MISO = MOSI;

 always @(posedge SCK)
 	begin
 		if (SSEL) begin
 			if (mem == 255) begin
 				mem <= 0;
 			end else begin
 				mem <= mem + 1;
 			end
 		end
 	end
 endmodule

