# 学习笔记 2026/5/19

## 学习内容

### Linux系统
1. Ubuntu的安装与配置
    
    因为手头上没有多的U盘做启动盘，暂时没有安装windows和linux双系统。~~就快搞好了~~

    目前是使用VM Ware安装了Ubuntu 22.04 LTS

2. Linux的终端命令学习

    学习了ls , pwd , cd , mkdir , chmod等命令的使用方法       ~~rm rf /*~~

    花了挺久才搞懂linux的文件权限。

|权限符号|数字值|对文件的作用|对目录的作用|
|----|----|----|----|
|r （读）|4|查看文件内容（如 cat, less）|列出目录内容（如 ls 需要同时有 x 权限才能打开目录）|
|w（写）|2|	修改、删除、重命名文件（删除受父目录权限影响）|	在目录中创建、删除、重命名文件/子目录（需要同时有 x 权限）
|x（执行）|1|执行文件（脚本或二进制程序）|进入目录（cd），以及访问目录下的文件（需要知道文件名）


### CMake
1. 语法系统

    CMake中所有的变量都默认是字符串

    使用变量的值时，用`${变量名}`的形式

    需要分隔的地方，可以用空格或者分号。e.g.
        `set( aa )`

2. 基础命令

```CMake
cmake_minimum_required ( VERSION 版本号 )       # 设置所需的最小cmake版本
project( 项目名 版本 ...)                       # 设置项目信息
add_executable(test main.cpp math.cpp)       # 添加可执行文件
add_library(test STATIC ...)          # 编译为静态库
target_include_directories(my_app PRIVATE include/)  # 为特定目标添加头文件搜索路径
target_link_libraries(my_app PRIVATE my_lib)        # 链接到静态库
add_subdirectory(src)                 # 添加子目录(必须有下一级CMakeList.txt)
find_package(OpenCV REQUIRED)         # 查找系统库
...
```

3. 困难

    CMake的语法有点令人难绷，从完全看不懂到能稍微理解就已经力竭了

    脚本有相当一部分都是AI写的。

    make了半天最后发现CMakeLists.txt打错了