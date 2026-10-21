function delta = computeDelta(Features1,Features2)
    %Features1 = table2array(removevars(Features1,"SensorName"));
    %Features2 = table2array(removevars(Features2,"SensorName"));
    delta = norm(Features2-Features1,'fro');
end