function plot_dt_IntersampleInterval(dt)
    % Plot the intersample interval
    figure();
    plot(dt-1);
    title("error of the intersample interval from 1 sec");
    ylabel("seconds of error");
    xlabel("interval");
    set(gca,'XScale','linear','YScale','log');
end