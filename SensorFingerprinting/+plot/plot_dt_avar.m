function plot_dt_avar(dt_stats)
    %Plot the Allan Variance of the clock
    figure();
    hold on;
    plot(dt_stats.dt_tau, dt_stats.dt_avar, 'b');
    plot(dt_stats.dt_tau, dt_stats.yfit, 'r--', 'LineWidth', 2);
    title("Population Allan Variance for the Intersample Interval Duration");
    xlabel('\tau');
    ylabel('AVar(\tau)');
    legend("Measured", "Trendline");
    set(gca,'XScale','log','YScale','log');
    grid on;
    hold off;
    disp("LogLog Slope:" + dt_stats.slope);
    disp("LogLog Intercept:" + dt_stats.intercept);
    disp("AVAR(\tau)=" + dt_stats.intercept +"\tau^"+dt_stats.slope);
end