from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description() : 
    turtlesim_node = Node (
        package='turtlesim' , 
        executable='turtlesim_node' ,
        name='turtlesim',
        output='screen',
    )

    param_file = PathJoinSubstitution(
        [FindPackageShare('ros2_homework_basic_package'), 'config', 'params.yaml']
    )

    eight_move_node = Node (
        package='ros2_homework_basic_package' , 
        executable='eight_move' , 
        name='eight_move',
        output='screen' , 
        parameters=[param_file],
    )

    return LaunchDescription([
        turtlesim_node , 
        eight_move_node,
    ])

"""
总共启动2个节点，1个参数文件
turtlesim: 海龟运动的模拟节点
eight_move: 向海龟发送运动指令的节点
"""
    