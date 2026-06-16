%% 第二问：轨迹跟踪
clear; clc; close all

% 车辆参数
lfr = 2.168 + 1.907; % 轴距 L
dt = 0.01;
v = 15; 
sim_steps = 2000;

% 参考轨迹 (正弦曲线)
X_ref = 0:0.1:200; 
Y_ref = 10 * sin(X_ref / 15); 

% 初始车辆状态 
X = X_ref(1); Y = Y_ref(1) + 3; phi = 0; 
X_vec = zeros(1, sim_steps); Y_vec = zeros(1, sim_steps);

Ld = 5; % 前视距离Ld = 5
for ii = 1:sim_steps
    X_vec(ii) = X; Y_vec(ii) = Y;
    
    % ===============================================================
    
    % ================= TODO 2.1: 实现某种跟踪算法 =================

    disx = X_ref - X;
    disy = Y_ref - Y;
    dis = sqrt(disx.*disx + disy.*disy); % 计算轨迹上所有点到当前车位置的距离
    xx = find(X_ref >= X , 1 , 'first'); % 找到X_ref中比当前点后的第一个点。而dis和X_ref共享一套索引。
    
    % 从当前点开始，找距离最接近前视距离的点
    minn = 5; % 所有的距离都应该在前视距离附近，因此初始设为前视距离
    minj = xx; % 目标点的索引
    % 因为要找到距离最接近的点，同时要保留索引，因此选择一个一个找
    for j = xx:1: min(xx+50 , 2000) % 防越界。X_max - X > Ld = 5 = 50 * 0.1
        if abs(dis(j) - Ld) < minn  
            minn = abs(dis(j) - Ld);
            minj = j;
        end
    end
    
    % 计算当前车轴与目标点的夹角alpha
    alpha = atan((Y_ref(minj) - Y)/(X_ref(minj) - X)) - phi;
    err = Ld * sin(alpha); % 横向误差
    sigma = atan(2*lfr/Ld/Ld * err);  % 代入公式
    % sigma = atan(2 * L * sin(alpha) / Ld) 也可以不引入横向误差计算

    % ===============================================================

    % ================= TODO 2.2: 车辆状态更新 =================
    % 提示: 将刚才求得的转向角 sigma 代入运动学模型（复用第一问代码），更新 X, Y, phi。
    phi_dot = v * tan(sigma) / lfr;
    phi = phi + phi_dot * dt;
    X = X + v * cos(phi) * dt ;
    Y = Y + v * sin(phi) * dt;
    % ===============================================================
    
    % 到达终点提前结束
    if X >= X_ref(end), break; end
end

% 绘图对比
figure; hold on; grid on;
plot(X_ref, Y_ref, 'k--', 'LineWidth', 2);
plot(X_vec(1:ii), Y_vec(1:ii), 'r-', 'LineWidth', 2);
legend('参考规划轨迹', '实际行驶轨迹');
title(['Pure Pursuit 跟踪 (Ld = ', num2str(Ld), 'm)']);
xlabel('X [m]'); ylabel('Y [m]'); axis equal;