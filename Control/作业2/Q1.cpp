#include <iostream>
#include <Eigen/Dense>
#include <cmath>

int main() {
    double lr[4] = {0.005, 0.01, 0.02, 0.05};      // 学习率
    double tol = 1e-3;      //允许误差设为0.001
    int max_epoch = 10000;  //最大迭代次数
    
    //X = [x , y]^T
    for (int i = 0; i < 4; i++) { // 遍历不同的学习率
        int epoch = 0;
        Eigen::Vector2d X(0.0, 0.0);   //初始位置
        Eigen::Vector2d target(3.0, 3.0);  //目标位置
        while (epoch < max_epoch) {    //使用while循环进行迭代
            Eigen::Vector2d grad;   //计算梯度
            grad(0) = X(0) - 3.0;   //x的梯度 = x-3
            grad(1) = 10.0 * (X(1) - 3.0);  //y的梯度 = 10*(y-3)
        
            X = X - lr[i] * grad;  //梯度下降更新位置。新位置 = 旧位置 - 学习率 * 梯度
            epoch++;
        
            if ((X - target).norm() < tol) {
                break;  //距离小于允许误差则停止迭代
            }
        }
        std::cout << "学习率: " << lr[i] << "\n";
        std::cout << "迭代次数: " << epoch << "\n";
        std::cout << "最终位置: (" << X(0) << ", " << X(1) << ")" << "\n";
        std::cout << "距离: " << (X - target).norm() << "\n\n";
        
    }
    
    
    return 0;
}