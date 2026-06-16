/**
 * @file Q3.cpp
 * @brief 使用 OSQP 求解器求解带不等式约束的二次规划（QP）问题
 *
 * ========== 数学问题描述 ==========
 *
 * 最小化（目标函数）：
 *     f(x, y) = 1/2 * (x² + 10·y²) - 3x - 30y
 *
 * 约束条件：
 *     x + y ≤ 4
 *
 * ========== OSQP 标准形式 ==========
 *
 * OSQP 求解的标准二次规划形式为：
 *
 *     minimize    0.5 * Xᵀ·P·X + qᵀ·X
 *     subject to  l ≤ A·X ≤ u
 *
 * 其中：
 *     P ∈ Rⁿˣⁿ  —— Hession 矩阵（对称半正定），定义二次项系数
 *     q ∈ Rⁿ     —— 梯度向量，定义一次项系数
 *     A ∈ Rᵐˣⁿ  —— 约束矩阵，将变量映射到约束空间
 *     l, u ∈ Rᵐ —— 约束的上下界
 *     X ∈ Rⁿ     —— 决策变量（本例中 n=2, 即 x 和 y）
 *     m          —— 约束个数（本例中 m=1）
 *
 * 本例对应关系：
 *     P = [[1,  0],     ← 0.5 * (1·x² + 10·y²) → 二次项系数
 *          [0, 10]]
 *     q = [-3, -30]ᵀ    ← -3x - 30y → 一次项系数
 *     A = [[1, 1]]      ← x + y → 约束的线性映射
 *     l = (-∞, )        ← 下界无约束
 *     u = (4, )         ← x + y ≤ 4
 *
 * ========== CSC 稀疏矩阵存储格式说明 ==========
 *
 * OSQP 使用 CSC（Compressed Sparse Column，压缩稀疏列）格式存储稀疏矩阵。
 * CSC 格式的三个数组含义：
 *
 *     P_x (data):  按列存储的非零元素值
 *     P_i (indices): 各非零元素的行索引
 *     P_p (colptr):  列指针数组，P_p[j] 表示第 j 列第一个非零元素
 *                    在 P_x/P_i 中的起始位置，最后一个元素 = 非零元总数
 *
 * 例如 diag(1, 10) 的 CSC 表示：
 *     P_x = [1.0, 10.0]     ← 非零值：第0列=1.0, 第1列=10.0
 *     P_i = [0, 1]          ← 行索引：1.0 在第0行, 10.0 在第1行
 *     P_p = [0, 1, 2]       ← 列指针：第0列从位置0开始,
 *                              第1列从位置1开始, 共2个非零元
 */

#include <iostream>
#include <vector>
#include "osqp.h"

int main() {
   
    OSQPInt n = 2;   //决策变量个数
    OSQPInt m = 1;   //约束条件个数

    //代价函数: F(X) = 1/2 * X^T * P * X + q^T * X

    /* 
    P = [[1,  0],
         [0, 10]]
    表示代价函数的二次项: X^T * P * X =  1/2 * (x^2 + 10 * y^2)
    */
    //用 CSC 格式构造稀疏矩阵 P(2*2)：
    std::vector<OSQPFloat> P_x = {1.0, 10.0};   //data:   非零元素值1,10
    std::vector<OSQPInt>   P_i = {0, 1};         //indices: 各非零元对应的行号0,1
    std::vector<OSQPInt>   P_p = {0, 1, 2};      //colptr:  列指针（第0列从索引0开始, 第1列从索引1开始, 共2个非零元）
    /*
    CSC矩阵由三个数组组成: data , indices , colptr
        data: 存储非零元素的值，按列顺序排列
        indices: 存储对应非零元素的行索引
        colptr: 存储每列第一个非零元素在 data 和 indices 中的起始位置，最后一个元素等于非零元素总数
    */
    //创建一个 n×n (2×2) 的 CSC 稀疏矩阵，包含 2 个非零元素
    OSQPCscMatrix* P = OSQPCscMatrix_new(n, n, 2, P_x.data(), P_i.data(), P_p.data());

    //q = [-3, -30]^T
    //表示一次项: -3 * x - 30 * y
    std::vector<OSQPFloat> q = {-3.0, -30.0};

    //A = [[1, 1]]  表示x + y <= 4 的约束
    //CSC矩阵
    std::vector<OSQPFloat> A_x = {1.0, 1.0};     //非零元素值1,1
    std::vector<OSQPInt>   A_i = {0, 0};          //各非零元对应的行号0,0
    std::vector<OSQPInt>   A_p = {0, 1, 2};       //列指针（第0列从索引0开始, 第1列从索引1开始, 共2个非零元）
    //创建一个 m×n (1×2) 的 CSC 稀疏矩阵，包含 2 个非零元素
    OSQPCscMatrix* A = OSQPCscMatrix_new(m, n, 2, A_x.data(), A_i.data(), A_p.data());

    //inf <= A·X <= 4
    std::vector<OSQPFloat> l = {-OSQP_INFTY};   //下界-inf
    std::vector<OSQPFloat> u = {4.0};            //上界:4.0,即 A·X <= 4

    //创建默认的求解器设置对象
    OSQPSettings* settings = OSQPSettings_new();
    osqp_set_default_settings(settings); //初始化默认设置
    settings->verbose = false; //关闭求解器输出日志

    //设置求解器
    OSQPSolver* solver;
    //目标函数P,q;约束A, l, u;维度m, n;配置settings。用来设置求解器
    osqp_setup(&solver, P, q.data(), A, l.data(), u.data(), m, n, settings);

    //调用OSQP的核心求解
    osqp_solve(solver);

    //检查是否成功求解。即OSQP_SOLVED
    if (solver->info->status_val == OSQP_SOLVED) {
        //结果
        double x_opt = solver->solution->x[0];
        double y_opt = solver->solution->x[1];

        std::cout << "\n求解成功！" << std::endl;
        std::cout << "最优解: x = " << x_opt << ", y = " << y_opt << std::endl;
        //计算目标的最优值
        std::cout << "目标函数值: "
                  << 0.5*(x_opt*x_opt + 10*y_opt*y_opt) - 3*x_opt - 30*y_opt
                  << std::endl;
    }

    osqp_cleanup(solver);
    OSQPCscMatrix_free(P);
    OSQPCscMatrix_free(A);
    OSQPSettings_free(settings);//释放资源
    //system("pause");
    return 0;
}
