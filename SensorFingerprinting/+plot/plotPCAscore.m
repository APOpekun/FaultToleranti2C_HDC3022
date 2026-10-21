function plotPCAscore(score,explained)
    figure
    scatter(score(:,1),score(:,2),100,'filled')
    
    %text(score(:,1),score(:,2),allsensors)
    
    xlabel(['PC1 (' num2str(explained(1),'%.1f') '%)'])
    ylabel(['PC2 (' num2str(explained(2),'%.1f') '%)'])
    title('Sensor Fingerprint PCA')
    grid on
end