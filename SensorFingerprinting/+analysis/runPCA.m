function [coeff,score,latent,tsquared,explained,mu] = runPCA(features)
    if istable(features) 
        Xraw = table2array(removevars(features,"SensorName"));
    else
        Xraw = features;
    end
    % Remove non-informative columns
    goodCols = std(Xraw,0,1) > 0;
    X = Xraw(:,goodCols);
    
    if istable(features) 
        %inspect the removed columns
        featureNames = features.Properties.VariableNames;
        badCols = not(goodCols);
        featureNames(badCols);
    end
    
    % Normalize remaining columns
    X = normalize(X);
    
    [coeff,score,latent,tsquared,explained,mu] = pca(X);
end