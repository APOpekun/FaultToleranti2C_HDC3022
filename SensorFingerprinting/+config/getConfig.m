function cfg = getConfig()

cfg.path = "\\apporto.com\dfs\UHCL\Users\1915097_uhcl\Documents\Thesis\";
%file1 = "TimeTemp";
file2 = "TimeTemp_2026_Sep_06_Sun_13_59_53";
file3 = "TimeTemp_2026_Sep_07_Mon_10_00_49";
file4 = "TimeTemp_2026_Sep_08_Tue_14_31_01";
file5 = "TimeTemp_2026_Oct_05_Mon_18_05_09";
cfg.filenames = [file2;file3;file4;file5];

cfg.sensorNames = ["Temp1","Temp2","Temp3","Temp4","Temp5","Temp6","Temp7","Temp8"];

cfg.outlierThreshold = 0.25;

cfg.smoothingWindow = 120;

cfg.sampleRate = 1; % samples/second

end