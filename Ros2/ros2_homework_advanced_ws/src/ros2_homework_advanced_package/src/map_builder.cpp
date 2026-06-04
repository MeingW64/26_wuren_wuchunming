#include "rclcpp/rclcpp.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"
#include "geometry_msgs/msg/point.hpp"
#include "fsd_common_msgs/msg/map.hpp"
#include <chrono>
#include <vector>
#include <map>
#include <string>
#include <functional>

using namespace std::chrono_literals;//使用...ms作字面量

class MapBuilder : public rclcpp::Node
{
public :
    MapBuilder() : Node("map_builder")
    {
        mk_pub = this->create_publisher<visualization_msgs::msg::MarkerArray>("mk_pub" , 10);//创建发布者，发布类型为MarkerArray
		mk_sub = this->create_subscription<fsd_common_msgs::msg::Map>("/estimation/slam/map" , rclcpp::QoS(10).reliable(), std::bind(&MapBuilder::subMk, this , std::placeholders::_1));
		//创建订阅者。订阅类型为Map，QoS服务使用可靠。
		//别管为什么写这么长（
        //timer = this->create_wall_timer(100ms , std::bind(&MapBuilder::pubMk , this));
		this->id = 0;	//初始化节点id。

    }
private : 
	void pubMk(const std::vector<fsd_common_msgs::msg::Cone>& cones ,const std::string& color , const fsd_common_msgs::msg::Map::SharedPtr msg ,visualization_msgs::msg::MarkerArray& mk_arr)
	{
		std::map<std::string , std::vector<double>> c_rgba;
		c_rgba["yellow"] = {1.0, 1.0, 0.0, 1.0};   // 每个颜色对应的RGBA
		c_rgba["blue"]   = {0.0, 0.0, 1.0, 1.0};
		c_rgba["red"]    = {1.0, 0.0, 0.0, 1.0};
		c_rgba["unknown"]= {1.0, 1.0, 1.0, 1.0};

		for(auto i : cones)
		{
			visualization_msgs::msg::Marker marker;	//一个一个地生成marker再加到array里
			marker.header.frame_id = msg->header.frame_id;  //坐标系名字
			//marker.header.frame_id = "world";
			marker.header.stamp = msg->header.stamp;	//时间戳
			marker.id = ++this->id ;	//每次都id+1

			marker.type = visualization_msgs::msg::Marker::SPHERE;//marker类型
			marker.action = visualization_msgs::msg::Marker::ADD;  //添加marker

			marker.scale.x = 0.5;	//marker大小
			marker.scale.y = 0.5;
			marker.scale.z = 0.5;
			marker.pose.position = i.position; //marker坐标。使用Map中的

			marker.color.r = c_rgba[color][0]; //marker颜色
			marker.color.g = c_rgba[color][1];
			marker.color.b = c_rgba[color][2];
			marker.color.a = c_rgba[color][3];
			

			marker.lifetime = rclcpp::Duration::from_seconds(0.0);	//生命周期为无限长
			mk_arr.markers.push_back(marker);  //将写好的marker丢到array中
			
		}
		//不能在这里发布array。这样在rviz里面会造成所有marker频闪
		return;
	}
	void subMk(const fsd_common_msgs::msg::Map::SharedPtr msg)
	{
		visualization_msgs::msg::Marker delMk;
		delMk.action = visualization_msgs::msg::Marker::DELETEALL;	//定义一个删除所有marker的marker(
		visualization_msgs::msg::MarkerArray mk_arr;
		mk_arr.markers.push_back(delMk); 	//把这个marker放到array的最前面。rviz接收到这个marker时就会先把原来的marker全图了

		pubMk(msg->cone_blue , "blue" ,msg , mk_arr);	//一个个地处理Map中的cone[]
		pubMk(msg->cone_red , "red" ,msg , mk_arr);
		pubMk(msg->cone_unknown , "unknown" ,msg , mk_arr);
		pubMk(msg->cone_yellow , "yellow" ,msg , mk_arr);

		mk_pub->publish(mk_arr); //最后一次性将整个array发布给rviz。rviz大卫带
	}

    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr mk_pub;  //定义发布者和订阅者
	rclcpp::Subscription<fsd_common_msgs::msg::Map>::SharedPtr mk_sub;
    //rclcpp::TimerBase::SharedPtr timer;
	int id;  //用一个全局变量来记录marker的id
	
};

int main(int argc , char** argv)
{
    rclcpp::init(argc , argv);	//经典流程

    auto node = std::make_shared<MapBuilder>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}