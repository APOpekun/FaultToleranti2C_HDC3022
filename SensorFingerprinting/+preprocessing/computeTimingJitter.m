function [dt,dt_stats] = computeTimingJitter(TimeTemp)

    % Calculate intersample interval
    dt = diff(TimeTemp{:,"now"});

    % Allan variance analysis
    minTau=1;
    maxTau=floor(numel(dt)/2);
    pointsPerDecade=12;
    dt_tau = transpose(generateLogTau( ...
        minTau,maxTau, ...
        pointsPerDecade)); %Log spacing

    %compute the Allan Variance of the Intersample Interval Duration
    dt_avar = allanvar(dt,dt_tau); % tau , channel=1

    %Compute the slope of the clock Allan Variance over Tau
    idx = dt_tau >= 1 & dt_tau <= 1000;   % sample region

    % linear fit in log10-log10 space;
    valid = idx & isfinite(dt_avar) & (dt_avar > 0);

    p = polyfit( ...
        log10(dt_tau(valid)), ...
        log10(dt_avar(valid)), ...
        1);

    %create the best fit line
    yfit = 10.^( ...
        p(1)*log10(dt_tau) + p(2));

    %Predict the taus
    predictionTaus = 10.^(0:6)';
    predictedJitter = 10.^( ...
        p(1)*log10(predictionTaus) + p(2));


    %Save the data for output
    dt_stats = struct();

    dt_stats.dt_tau = dt_tau;
    dt_stats.dt_avar = dt_avar;

    dt_stats.slope = p(1);
    dt_stats.intercept = p(2);

    dt_stats.yfit = yfit;

    dt_stats.predictionTaus = predictionTaus;
    dt_stats.predictedJitter = predictedJitter;

    dt_stats.percentiles = 0:100;
    dt_stats.percentileValues = ...
        prctile(dt-1,dt_stats.percentiles);

end

function tau = generateLogTau(minTau,maxTau,pointsPerDecade)
    minDecade = log10(minTau);
    maxDecade = log10(maxTau);

    nPts = ceil((maxDecade-minDecade)*pointsPerDecade)+1;

    tau = unique(round( ...
        logspace(minDecade,maxDecade,nPts)));

    tau(tau > maxTau) = [];

end
