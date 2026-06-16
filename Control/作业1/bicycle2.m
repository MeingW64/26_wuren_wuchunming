Iz = 5633.44; % 横摆转动惯量
Cf = 100000;  % 前轮侧偏刚度
Cr = 100000;  % 后轮侧偏刚度
m = 1500;     % 车辆质量

X = 1; Y = 10; phi = 0; % 重置初始状态
x_dot = v; y_dot = 0; phi_dot = 0; % 初始速度状态
phi_vec = []; X_vec_dyn = []; Y_vec_dyn = [];

for ii = 1:5000
    phi_vec = [phi_vec, phi];
    X_vec_dyn = [X_vec_dyn, X];
    Y_vec_dyn = [Y_vec_dyn, Y];

    % 计算前后轮侧偏角
    alpha_f = sigma - (y_dot + lf * phi_dot) / x_dot;
    alpha_r = - (y_dot - lr * phi_dot) / x_dot;

    % ================= TODO 拓展: 动力学模型状态更新 =================
    % 提示: 
    % 1. 根据侧偏刚度计算横向轮胎力 Fyf, Fyr
    % 2. 根据牛顿第二定律计算横向加速度 y_ddot 和横摆角加速度 phi_ddot
    % 3. 积分更新速度 y_dot, phi_dot
    % 4. 将车体坐标系下的速度转换到全局坐标系下，更新 X, Y, phi

    Fyf = % [在此填空]
    Fyr = % [在此填空]

    y_ddot = % [在此填空]
    phi_ddot = % [在此填空]

    y_dot = % [在此填空]
    phi_dot = % [在此填空]

    phi = % [在此填空]
    X = % [在此填空]
    Y = % [在此填空]

    % ===============================================================
end
figure(1); hold on;
plot(X_vec_dyn, Y_vec_dyn, 'r.');
legend('Kinematic (运动学)', 'Dynamic (动力学)');
title("Kinematic vs Dynamic Bicycle Model (v = 30m/s)");