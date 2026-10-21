
%Analysis V2
clear
tic

%Create a shortcut to point to the rawdata
features=FingerprintMetaFunction(noise,allsensors)


%Rolling on the data
maxpts = 600; %seconds of window
windowpoints = 0:maxpts-1;
seconds=height(noise)-maxpts;
slices = 1:maxpts/2:seconds;
nWindows=length(slices)

for i=1:nWindows
    t=slices(i);
    noisewindow = noise(t+windowpoints,:);
    Features(i).Data = FingerprintMetaFunction(noisewindow,allsensors);
end




AllRows = [];
RejectedCols=['SensorName'];

for i = 1:nWindows
    F = removevars(Features(i).Data,'SensorName');
    VarNames = F.Properties.VariableNames;
    X = table2array(F);
    
    badcols = std(X)==0;
    if any(badcols)
        fprintf("Window %d has %d constant cols\n", ...
        i,sum(badcols));
        VarNames(badcols)
    end
end
    %X = normalize(X);
    %AllRows = [AllRows; X];

sum(isnan(AllRows),'all')
sum(isinf(AllRows),'all')
[nanRow,nanCol] = find(~isfinite(AllRows));
BadColumns = find(any(isnan(AllRows),1));
length(BadColumns)
AcceptedCols = Features(1).Data.Properties.VariableNames;
AcceptedCols(strcmp(AcceptedCols,"SensorName")) = [];
AcceptedCols(BadColumns)

% size(AllRows)
% rank(AllRows)
% rank(zscore(AllRows))
% max(abs(AllRows(:)))
% min(abs(AllRows(:)))
% std(AllRows)
% sum(std(AllRows)==0)
[CoeffGlobal,ScoreGlobal,latentGlobal,tsquaredGlobal,ExplainedGlobal,muGlobal] = pca(AllRows)

% FeatureNames = Features(1).Data.Properties.VariableNames;
% 
% FeatureNames(strcmp(FeatureNames,'SensorName')) = [];
% 
% GlobalGoodCols = true(size(FeatureNames));
% 
% for i = 1:nWindows
% 
%     Xraw = table2array(removevars(Features(i).Data,'SensorName'));
% 
%     GlobalGoodCols = ...
%         GlobalGoodCols & ...
%         (std(Xraw,0,1) > 0);
% 
% end
% 
% AcceptedCols = FeatureNames(GlobalGoodCols)
% 
% for i = 1:nWindows
% 
%     X = table2array( ...
%         Features(i).Data(:,AcceptedCols));
% 
%     X = zscore(X);
% 
%     [coeff,score,~,~,explained] = pca(X);
% 
% end

% featureNames = features.Properties.VariableNames
% %prefilter
% RejectedCols=['SensorName'];
% for i = 1:nWindows
%     Xraw = table2array(removevars(Features(i).Data,'SensorName'));
%     % Remove non-informative columns
%     goodCols = std(Xraw,0,1) > 0;
%     % X = Xraw(:,goodCols);
% 
%     %inspect the removed columns
%     featureNames = features.Properties.VariableNames;
%     badCols = not(goodCols);
%     RejectedCols = [RejectedCols featureNames(badCols)];
% end
% 
% RejectedCols=unique(RejectedCols)
% PCA_score = zeros([8 7 nWindows]);
% PCA_coeff = zeros([17 7 nWindows]);
% PCA_explained = zeros([1 7 nWindows]);
% for i = 1:nWindows
%     X = table2array(removevars(Features(i).Data,RejectedCols));
%     % Normalize remaining columns
%     X = normalize(X);
% 
%     [coeff,score,~,~,explained] = pca(X);
%     PCA_score(:,:,i) = score;
%     PCA_coeff(:,:,i)  = coeff;
%     PCA_explained(:,:,i)  = explained;
% end
% PCA_score
% PCA_coeff
% PCA_explained

% PCA
% 
% %Plot it with scatter 3
% PC1 = zeros(nWindows,8);
% PC2 = zeros(nWindows,8);
% PC3 = zeros(nWindows,8);
% PC4 = zeros(nWindows,8);
% PC5 = zeros(nWindows,8);
% PC6 = zeros(nWindows,8);
% PC7 = zeros(nWindows,8);
% PCSpread = zeros(nWindows,1);
% 
% for i = 1:nWindows
%     PC1(i,:) = PCA(i).score(:,1);
%     PC2(i,:) = PCA(i).score(:,2);
%     PC3(i,:) = PCA(i).score(:,3);
%     PC4(i,:) = PCA(i).score(:,4);
%     PC5(i,:) = PCA(i).score(:,5);
%     PC6(i,:) = PCA(i).score(:,6);
%     PC7(i,:) = PCA(i).score(:,7);
% end
% 
% 
% figure
% hold on
% 
% for sensor = 1:8
%     plot3(PC1(:,sensor),PC2(:,sensor),1:nWindows);
% end
% hold off
% xlabel('PC1')
% ylabel('PC2')
% zlabel('Time')
% title("Pc1 vs PC2 over time")
% grid on
% view(3)
% 
% 
% for i = 1:nWindows
%     PCSpread(i) = trace(cov(PCA(i).score(:,1:3)));
% end
% figure
% plot(PCSpread)
% xlabel("Spread")
% 
% 
% figure
% %Check for basis flips
% plot(PC1(:,1))
% xlabel("PC1")
% 
% figure
% scatter(PC1(:,1),PC2(:,1),5,1:length(PC1),'filled')
% colorbar
% xlabel('PC1')
% ylabel('PC2')
% 
% 
% figure
% scatter3(PC1(:,1), ...
%          PC2(:,1), ...
%          PC3(:,1), ...
%          5, ...
%          1:length(PC1), ...
%          'filled');
% xlabel('PC1')
% ylabel('PC2')
% zlabel('PC3')
