
module serial2tcp_loopback (
    input  wire sys_clk,
    output wire serial2tcp_source_valid,
    input  wire serial2tcp_source_ready,
    output wire [7:0] serial2tcp_source_data,
    input  wire serial2tcp_sink_valid,
    output wire serial2tcp_sink_ready,
    input  wire [7:0] serial2tcp_sink_data
);

assign serial2tcp_source_data = serial2tcp_sink_data;
assign serial2tcp_source_valid = serial2tcp_sink_valid;
assign serial2tcp_sink_ready = serial2tcp_source_ready;

endmodule
