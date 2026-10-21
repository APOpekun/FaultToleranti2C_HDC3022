function plotPCAscore3(score,explained)
    figure
    scatter3(score(:,1),score(:,2),score(:,3),100,'filled')
    
    %text(score(:,1),score(:,2),score(:,3),allsensors)
    
    xlabel(['PC1 (' num2str(explained(1),'%.1f') '%)'])
    ylabel(['PC2 (' num2str(explained(2),'%.1f') '%)'])
    zlabel(['PC3 (' num2str(explained(3),'%.1f') '%)'])
    title('Sensor Fingerprint PCA')
    grid on
end