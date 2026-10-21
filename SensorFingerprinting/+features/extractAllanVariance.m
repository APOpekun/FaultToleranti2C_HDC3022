function features = extractAllanVariance(noise,allsensors)
    features = table();
    features.SensorName = allsensors';
    nSensors = length(allsensors);

    % AllanMin = zeros(nSensors,1);
    % AllanMinTau = zeros(nSensors,1);
    
    %tau_in = 1:height(noise)/2;
    tau_in= unique(round(2.^(0:log2(size(noise,1)/2)/1000:log2(size(noise,1)/2))));
    [avar,tau]=allanvar(noise,tau_in); % tau channel
    
    [AllanMin,idx] = min(avar,[],1);
    AllanMinTau = tau(idx);
    
    AllanSlope = zeros(nSensors,1);
    AllanIntercept = zeros(nSensors,1);
    for k = 1:nSensors
        valid = avar(:,k) > 0;

        p = polyfit( ...
            log10(tau(valid)), ...
            log10(avar(valid,k)), ...
            1);

        AllanSlope(k) = p(1);
        AllanIntercept(k) = p(2);
    end
    
    features.AllanMin = AllanMin';
    features.AllanMinTau = AllanMinTau;
    features.AllanSlope = AllanSlope;
    features.AllanIntercept = AllanIntercept;
    
    for m = 1:length(tau)
        features.(sprintf('AVar_Tau_%d',tau(m))) = avar(m,:)';
    end
end

    
    % features.Properties.RowNames = allsensors;
    
    % figure
    % plot(tau,avar)
    % grid on;
    % legend
    % xlabel("tau");ylabel("Variance");
    % set(gca,'XScale','log','YScale','log');