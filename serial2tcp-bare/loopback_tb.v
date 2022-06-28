
module serial2tcp_loopback_tb ();

reg sys_clk;
wire serial2tcp_source_valid;
wire serial2tcp_source_ready;
wire [7:0] serial2tcp_source_data;
wire serial2tcp_sink_valid;
wire serial2tcp_sink_ready;
wire [7:0] serial2tcp_sink_data;

initial begin
    sys_clk = 0;
end

always #5 sys_clk = ~sys_clk;

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



