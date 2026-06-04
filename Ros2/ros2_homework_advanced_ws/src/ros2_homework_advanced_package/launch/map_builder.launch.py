from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare

def generate_launch_description() :
    map_builder_node = Node (
        package = 'ros2_homework_advanced_package' ,
        executable = 'map_builder',
        name = 'map_builder',
        output = 'screen',
    )

    rviz2_node = Node (
        package ='rviz2',
        executable='rviz2',
        name = 'rviz',
        output = 'screen',
        arguments = ['-d' , PathJoinSubstitution([FindPackageShare('ros2_homework_advanced_package'), 'config', 'rviz_init.rviz'])]
    )

    bag_play = ExecuteProcess(
        cmd = ['ros2' , 'bag' , 'play' ,PathJoinSubstitution([FindPackageShare('ros2_homework_advanced_package') , 'bag' , 'map_to_visualize_0.db3']) ]
    )

    return LaunchDescription ([
        map_builder_node,
        rviz2_node,
        bag_play,
    ])