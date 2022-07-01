module add (
    input sclk,
    input rst_n,
    input [7:0] data1_i,
    input [7:0] data2_i,
    output reg [7:0] data_o
);

always@ (posedge sclk or negedge rst_n) begin
    if(~rst_n)
        data_o <= 8'b0;
    else
        data_o <= data1_i + data2_i;
end

endmodule
