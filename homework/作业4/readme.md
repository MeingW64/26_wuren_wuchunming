k = 4
4聚类簇

X数据结构

i:第i个数据     x1      x2
    0          x1_0   x2_0
    1          x1_1   x2_1
    i          x1_i   x2_j
    j          x1_j   x2_j

distance函数
v1 :  x1_v1     x2_v1 --v1
x2 :  x1_v2     x2_v2


assignment
i : [x1 , x2 ,x3] , xn是ndarray , i是center的index

计算i到所有centers的距离，放到一个列表里，取最小值
centers: [c1 , c2 , c3 ,c4]



K_means

随机分配中心
每次训练:
    分类
    更新中心
    计算当前分类下的cost