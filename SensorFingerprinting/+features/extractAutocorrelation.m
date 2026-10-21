function features = extractAutocorrelation(noise,sensorsNames)
    features = table();
    features.SensorName = sensorsNames';

    nSensors = length(sensorsNames);

    %I want to see a lag sweep similar to the E6 or E12 scale for resistors
    %12/decade * (4-0)Decades +1 end = 12*4+1
    powers = [0 4];
    perdecade = 12;
    lags = unique(round(logspace(powers(1),powers(2),diff(powers)*perdecade+1)));
    nLags = length(lags);

    AC = zeros(nSensors,nLags);

    for k = 1:nSensors
        x = noise(:,k);
        maxLag = max(lags);
        r = xcorr(x,maxLag,'coeff');
        % MAX LAG is one point so why am I making a lags array
        zeroLag = maxLag+1;
        AC(k,:) = r(zeroLag + lags);
    end
    varNames = compose("AC_%d",lags);

    ACtable = array2table(AC,...
        'VariableNames',cellstr(varNames));
    
    features = table(sensorsNames',...
        'VariableNames',{'SensorName'});
    
    features = [features ACtable];
    % features = addvars( ...
    %     features,...
    %     allsensors',...
    %     'Before',1,...
    %     'NewVariableNames', ...
    %     "SensorName");
end
% AC1 = zeros(nSensors,1);
% AC10 = zeros(nSensors,1);
% AC1(k)  = r(12);   % lag = 1
% 
% AC10(k) = r(end);  % lag = 10
% features.AC1 = AC1;
% features.AC10 = AC10;
