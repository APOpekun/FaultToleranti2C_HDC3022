function [robustAvgSmoothGauss,robustAvg] = computeRobustAverage(data,timestrip,cfg)
    % 0. Compute the Per Row Median
    Median=median(data,2);
    % 1. Compute deviation from median
    MedianDifference = abs(data) - Median;
    % 2. Build mask of good sensors
    Mask = MedianDifference <= cfg.outlierThreshold;   % Nx8 logical
    % 3. Zero out bad sensors
    goodVals = data .* Mask;
    % 4. Count good sensors per row
    numGood = sum(Mask, 2);
    % 5. Handle rows with zero good sensors
    
    robustAvg = NaN(size(numGood));
    idx = numGood > 0;
    % 6. Compute robust average
    robustAvg(idx) = sum(goodVals, 2) ./ numGood;
    
    % Smooth robustAvg data
    [robustAvgSmoothGauss,winSize] = smoothdata(robustAvg,"gaussian",cfg.smoothingWindow,"SamplePoints",timestrip);
end
