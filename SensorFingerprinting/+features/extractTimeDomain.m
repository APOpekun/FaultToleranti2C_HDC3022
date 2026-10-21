function features = extractTimeDomain(noise,allsensors)
    features = table();
    features.SensorName = allsensors';

    features.Mean     = mean(noise)';
    features.StdDev   = std(noise)';
    features.Skew     = skewness(noise)';
    features.Kurtosis = kurtosis(noise)';
    features.RMS      = rms(noise)';
    features.MAD      = mad(noise)';
    features.IQR      = iqr(noise)';
    
    % features.Properties.RowNames = allsensors;
end