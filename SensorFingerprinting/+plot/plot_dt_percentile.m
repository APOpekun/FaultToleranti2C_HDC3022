function plot_dt_percentile(dt_stats)
    %Plot the percentiles
    figure();
    scatter(dt_stats.percentiles,dt_stats.percentileValues);
    set(gca,'XScale','linear','YScale','log');
    xlabel("Percentile");
    ylabel("dt Error from 1");
end