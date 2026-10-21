function plot_dt_boxchart(dt)
    % % Create boxchart of dt
    figure(); boxchart(dt-1,'Notch','on',"DisplayName","dt-1");
    % Add ylabel, title, and legend
    ylabel("dt-1");
    title("Summary of the error of the intersample interval from 1 sec")
    set(gca,'YScale','log');
    legend
end