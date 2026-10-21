function features = extractPowerSpectralDensity(noise,allsensors)
    features = table();
    features.SensorName = allsensors';

    nSensors = length(allsensors);

    Fs = 1;   % Replace with actual sample rate %current sample rate is 1Hz
    centroid  = zeros(nSensors,1);
    spectralVar = zeros(nSensors,1);
    spectralSkew = zeros(nSensors,1);
    peakfreq  = zeros(nSensors,1);
    totpower  = zeros(nSensors,1);
    entropyPSD = zeros(nSensors,1);
    noiseSlope = zeros(nSensors,1);
    noiseIntercept = zeros(nSensors,1);
    
    fBands = [
    0      0.001;
    0.001  0.003; 0.003 0.005; 0.005 0.01;
    0.01   0.03; 0.03   0.05;  0.05  0.1;
    0.1    0.3;  0.3    0.5;   0.5   1;
    ];
    bandEnergy = zeros(nSensors,size(fBands,1));
    
    for k = 1:nSensors
        [pxx,f] = pwelch(noise(:,k),[],[],[],Fs);
    
        centroid(k) = sum(f.*pxx)/sum(pxx);%Spectral Mean
        spectralVar(k) = sum((f-centroid(k)).^2 .* pxx)/sum(pxx);%Spectral Variance
        spectralSkew(k) = sum((f-centroid(k)).^3 .* pxx)/(sum(pxx)*spectralVar(k)^(1.5)); %SpectralSkew
    
        [~,idx] = max(pxx);
        peakfreq(k) = f(idx);
        totpower(k) = bandpower(pxx,f,'psd');
        
        valid = f > 0 & pxx > 0;
        fit = polyfit(log10(f(valid)),log10(pxx(valid)),1);
        noiseSlope(k) = fit(1);
        noiseIntercept(k) = fit(2);
        
        for b = 1:size(fBands,1)
            idx = f >= fBands(b,1) & f <  fBands(b,2);
            bandEnergy(k,b) = sum(pxx(idx));
        end

        p = pxx/sum(pxx);
        valid = p > 0;
        entropyPSD(k) = -sum(p(valid).*log2(p(valid)));
    end

    features.SpectralCentroid = centroid;
    features.SpectralVariance = spectralVar;
    features.SpectralSkew = spectralSkew;
    features.PeakFreq = peakfreq;
    features.TotalPower = totpower;
    features.SpecEntropy = entropyPSD;
    features.OneOverF_Slope = noiseSlope;
    features.OneOverF_Intercept = noiseIntercept;
    
    for b = 1:size(fBands,1)
        features.(sprintf('FFTBand_%d',b)) = bandEnergy(:,b);
    end


end

%Pending for PSD
% [pks,locs] = findpeaks(pxx,f,...
%     'SortStr','descend');
% 
% NPeaks = min(5,length(pks));
% Peak1Freq
% Peak1Mag
% Peak2Freq
% Peak2Mag
% ...

% features.Properties.RowNames = allsensors;

% plot all eight PSDs on the same log-log axes.
% figure;
% hold on
% for k = 1:nSensors
%     [pxx,f] = pwelch(noise(:,k),[],[],[],Fs);
%     plot(f,pxx)
% end
% hold off
% legend(allsensors,"Location","northwest")
% grid on
% set(gca,'XScale','log','YScale','log');
% xlabel('Frequency');ylabel('PSD');title('Sensor Noise Spectra')

% fftFrequencies = [
% 1e-4
% 2e-4
% 5e-4
% 1e-3
% 2e-3
% 5e-3
% 1e-2
% 2e-2
% 5e-2
% 1e-1
% ];
%Interpolate the PSD:
% psdSample = interp1(f,pxx,...
%                     fftFrequencies,...
%                     'linear',...
%                     'extrap');
