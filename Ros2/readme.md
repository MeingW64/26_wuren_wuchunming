# ros学习笔记

## 1.工作区结构

- 总文件夹
    - build                     编译过程文件目录 
    - install                   可执行文件目录
    - log                       编译日志目录
    - src                       源文件目录
        - package1              功能包
        - package2
            - src
                - xxx.cpp       可执行文件
            - config            用来存放配置文件。包括参数，rviz配置文件等
            - launch            用来存放启动文件
            - CMakeLists.txt    
            - package.xml       功能包清单

其中，config, launch等文件夹也要编译到install目录下，否则生成的节点也无法调用它们的内容
install目录下会有local_setup.bash文件，用来将里面的东西都注册到ros2中。每一次启动都要`source install/local_setup.bash`

## 2.节点创建流程

1. 初始化ros2客户端
2. 创建节点对象
3. 使用spin函数保持节点对象活跃
4. 结束后，释放节点

自定义的节点类要继承 `rclcpp::Node`
类内部一般定义 
1. 订阅者 用来订阅topic，得到话题中的数据。一般要绑定回调函数，在得到数据时进行下一步操作
2. 发布者 用来发布topic。可以绑定计时器，定时发布话题。
3. 计时器

更多的笔记，可以参考Ros2目录下的`Ros2笔记.zip`。这个从笔试前就开始记了。
---
# 作业1

## 代码启动流程
```
cd ros2_homework_advanced_ws
colcon build
source install/local_setup.bash

ros2 launch ros2_homework_basic_package eight_move.launch.py
```

## 完成思路
小海龟：？！弓虽虽弓 ！？
伟大的先人写好了turtlesim，还留下了用来操纵小海龟的节点，那还说啥了？直接上话题狠狠写入。
创建一个节点用来发布海龟运动用的角速度和线速度，发送到/turtle1/cmd_vel。嘛，发送的格式就用twist。
要让海龟做8字运动，其实就是两个相反的圆周。设置恒定的线速度，大小恒定的角速度。每当小海龟运动一个圆周，就让角速度反向
可以用三角函数取符号来实现角速度的方向变换。相位可以用计时器来计算。

## 困难
看的教程里面是用python写的。灵机一动，为何不用更有操作的c++呢？
自己从0对着模板搓节点也有点难。很多不懂的地方要问ai。
猪脑过载半天才推出公式。拼尽全力无法跑对，猛觉角速度的单位是弧度制。
---
# 作业2

## 代码启动流程
```
cd ros2_homework_advanced_ws
colcon build
source install/local_setup.bash

ros2 run ros2_homework_advanced_package map_builder
rviz2
cd src/ros2_homework_advanced_package/bag
ros2 bag play map_to_visualize_0.db3
```
或者，也可以用我写的launch
```
ros2 launch ros2_homework_advanced_package map_builder.launch.py
```

## 完成思路
欸，使用bag命令能播放之前的话题，那我用一个节点监听这个话题，消化成marker再转发给rviz就好了吗？
这个话题的msg里面全是cone[]，但其中只有color和position对生成marker有用
写一个字符串到数组的映射colorMap，字符串对应颜色名，数组里面储存RGBA对应的值。用来写marker的颜色
用一个函数，一次性处理一个颜色的cone[]。里面一个个地生成marker后加入marker_array中。最后一次性发送给rviz
rviz里面的坐标系和msg里面的坐标系名字不一样。把rviz配置好后保存配置文件，用launch文件根据配置文件启动rviz。这样启动的时候就默认是world坐标系了（
其实这个colorMap也是能用参数文件写入的。但是comming s $\infty$ n

## 困难
由于神秘原因，无法编译fsd_common_msgs这个包。抓耳挠腮让ai看，改了半天cmaklists里面的路径都没用
最后突发奇想把整个包复制到全英文路径下就编译成功了。hyw？上一个作业里还编译得好好的呢？整个路径里唯一的中文是"桌面"！？
什么叫这个msg里面全是数组？什么叫我一个一个marker发送就会让一万个锥桶叠在一起，还会让一堆锥桶不显示？
什么叫msg里面掺了不属于这个world的点？
最后听了同学的劝，把一个一个marker发送的写法（本质屎山）换成了一次性发送一个marker_array的写法
甚至在发送前加了一个用来DELETEALL的点，把之前显示的点全图了（笑