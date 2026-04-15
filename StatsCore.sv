`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/15/2026 05:00:04 PM
// Design Name: 
// Module Name: StatsCore
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module StatsCore(
    input [17:0] in0,
    input [17:0] in1,
    input [17:0] in2,
    input [17:0] in3,
    input [3:0] valid,
    output [17:0] MeanOut,
    input       clk,
    input       rst,
    input       load
    );
    
    // ============================================================
    // Stage 0: Input registers (V1..V4)
    // ============================================================

    reg [23:0] V0, V1, V2, V3;

    always @(posedge clk) begin
        if (rst) begin
            V0 <= 0;
            V1 <= 0;
            V2 <= 0;
            V3 <= 0;
        end
        else if (load) begin
            V0 <= valid[0] ? {3'b000, in0, 3'b000}: 24'h000000;
            V1 <= valid[1] ? {3'b000, in1, 3'b000}: 24'h000000;
            V2 <= valid[2] ? {3'b000, in2, 3'b000}: 24'h000000;
            V3 <= valid[3] ? {3'b000, in3, 3'b000}: 24'h000000;
            // expand 18→24 bits
        end
    end
    // ============================================================
    // Stage 1: Compute mean
    // ============================================================
    reg [23:0] sum_s1;
    reg [23:0] mean_s1;

    always @(posedge clk) begin
        if (rst) begin
            sum_s1 <= 0;
            mean_s1 <= 0;
        end 
        else begin
            sum_s1 <=(V0+V1)+(V2+V3);
            mean_s1 <= sum_s1 / (valid[3]+valid[2]+valid[1]+valid[0]);
        end
    end
    
endmodule


