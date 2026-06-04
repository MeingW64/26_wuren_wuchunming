#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp" //twist消息
#include <chrono> //用来获取时间的库
//#include "memory" //内存管理库。可使用智能指针等功能。rclcpp里面自带智能指针。
#include <functional>
#include <cmath>

using namespace std::chrono_literals;

//using namespace rclcpp;
class EightMove : public rclcpp::Node
{
public :
    EightMove() : Node("eight_move")
    {
        v = this->declare_parameter<double>("v" , 2) ;  //初始化类参数，要么从yaml导入参数，要么使用默认值
        omiga = this->declare_parameter<double>("omiga" , 2);   
        v_agl = this->declare_parameter<double>("v_agl" , 1);

        pub = this->create_publisher<geometry_msgs::msg::Twist> ("/turtle1/cmd_vel" , 30);  
        //创建发布节点。发送到turtle1/cmd_vel。30是命令栈的深度
        tmr = this->create_wall_timer( 50ms , std::bind(&EightMove::move , this));
        //创建计时器
        //将发布器设置为定时发送

        begin = this->get_clock()->now();  //节点初始化时的时间。相当于运动开始的时间，用来计算周期
    }
private :
    rclcpp :: TimerBase :: SharedPtr tmr;
    rclcpp :: Publisher <geometry_msgs :: msg :: Twist> :: SharedPtr pub;

    double v;       //线速度
    double omiga;   //角频率
    double v_agl;   //角速度
    rclcpp :: Time begin;

    void move()
    {
        rclcpp::Time now = this->get_clock()->now();  //
        
        double dt = (now - begin).seconds();

        geometry_msgs::msg::Twist msg;
        msg.linear.x = v;          // 恒定线速度
        msg.angular.z = v_agl * (sin(omiga* dt / 4)>0 ? 1 : -1);
        //每次走完一个圆周(半个sin周期)后，让线速度反向

        RCLCPP_INFO(this->get_logger() , "线速度:%.2f  角速度:%.2f" , msg.linear.x , msg.angular.z);
        pub->publish(msg);//发送消息
    }
};
int main(int argc , char **argv)
{
    rclcpp::init(argc , argv);//初始化ros2通信

    auto node = std::make_shared<EightMove>(); //创建节点

    rclcpp::spin(node); //用spin函数保证节点能在等待调用时也能执行其他任务，保持活跃

    rclcpp::shutdown(); //关闭节点
    return 0;
}