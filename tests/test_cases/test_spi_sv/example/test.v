`timescale 1ns/1ps

module test();

reg clk;

reg rst_n;

reg [7:0] data1_i;

reg [7:0] data2_i;

wire [7:0] data_o;

initial begin
    $dumpfile("test.vcd");
    $dumpvars;
end

initial begin
    clk = 0;
    forever #5 clk = ~clk;
end

initial begin
    rst_n = 0;
    data1_i = 0;
    data2_i = 0;

    #100
    rst_n = 1;

    repeat(20) begin
        @(posedge clk) begin
            data1_i <= data1_i + 8'd1;
            data2_i <= data2_i + 8'd2;
        end
    end

    #500
    $stop;

end

add u_add(
    .sclk( clk ),
    .rst_n( rst_n ),
    .data1_i( data1_i ),
    .data2_i( data2_i ),
    .data_o ( data_o )
);

endmodule