function datafeatures=extractFingerprint(noise,sensorsNames)
    
    features1 = features.extractTimeDomain(noise,sensorsNames);
    features2 = features.extractAutocorrelation(noise,sensorsNames);
    features3 = features.extractPowerSpectralDensity(noise,sensorsNames);
    features4 = features.extractAllanVariance(noise,sensorsNames);

    features12 = join(features1,features2);
    features34 = join(features3,features4);
    datafeatures = join(features12,features34);
end