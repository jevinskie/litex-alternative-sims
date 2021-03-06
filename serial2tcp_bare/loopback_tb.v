`timescale 1ns/1ps

module serial2tcp_loopback_tb ();

reg sys_clk;
wire serial2tcp_source_valid;
wire serial2tcp_source_ready;
wire [7:0] serial2tcp_source_data;
wire serial2tcp_sink_valid;
wire serial2tcp_sink_ready;
wire [7:0] serial2tcp_sink_data;

// reg [8*100:1] line;

initial begin
    $display("initial");

    // $fgets(line,'h8000_0000);

    sys_clk <= 0;
    // $vpi_tree;
end

always #5 sys_clk <= ~sys_clk;

// counter
reg [7:0] cnt;
initial begin
    cnt <= 0;
end

always @(posedge sys_clk) begin
    $display("posedge sys_clk");
    cnt <= cnt + 1;
end

assign serial2tcp_sink_data = cnt;

serial2tcp_loopback loopback(
    sys_clk,
    serial2tcp_source_valid,
    serial2tcp_source_ready,
    serial2tcp_source_data,
    serial2tcp_sink_valid,
    serial2tcp_sink_ready,
    serial2tcp_sink_data
);

endmodule



