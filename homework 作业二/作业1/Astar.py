import numpy as np
import random
import matplotlib.pyplot as plt
import tkinter as tk
import sys
import os
import time

'''
代码来自于 : https://www.cnblogs.com/quantoublog/articles/15819455.html。
源代码有很多相关注释，都被我删了。关于算法的注释都是我自己写的

算法用于模拟二维地图中的最短路寻路。地图由离散的格子组成。原程序中可以向8个方向搜索，我把它改成只能向4个方向搜索的了。

变量
Node : 用于存放格子的二维数组
AStarNode : 每个格子的定义类，类内包括:
    g : 走到该格子时已付出的代价
    h : 当前格子到终点的预估代价。代码中默认采用曼哈顿距离计算预估代价。h在本节点被搜索到时计算得出
        对于曼哈顿距离 : h = |x0 - x| + |y0 - y|
        对于欧式距离 : h = sqrt ( (x0 - x) ^ 2 + (y0 - y) ^ 2) )
    f : f = g + h 用于评估该节点作为下一个搜索节点的优先级。初始时，所有都为0

A*算法主体程序 : 第90行
判断子结点的函数 : 第161行

'''

mapRow = 0
mapCol = 0

openlist = []   # 存储候补节点的列表
closelist = []  # 存储已经搜索过的节点的列表

nodes = {}

menuNode = -1
buttonNodes = {}

startRow, startCol, endRow, endCol = 0, 0, 0, 0

ispause = False
# 当前搜索方法,默认曼哈顿（Manhattan ），欧氏距离（Euclidean）
findMethod = "Manhattan"
methodButton1, methodButton2 = 0, 0

# 定义格子类
class AStarNode:
    def __init__(self):
        self.row = -1
        self.column = -1
        self.f = 0
        self.g = 0
        self.h = 0
        self.type = 'walk'
        self.father = None
        self.value = 0
    def setPos(self,row,column):
        self.row = row
        self.column = column
        # 设置node状态，walk可走，stop不可
    def setType(self,type):
        self.type = type

def ShowNodes(w,h):
    global mapRow,mapCol,nodes,openlist,closelist
    for i in range(w):
        for j in range(h):
            print(nodes[i,j].type, end='\t')
        print()
def ShowResultMap(w, h, pathlist):
    global nodes
    for p in pathlist:
        nodes[p.row,p.column].type = "gogo"
    for i in range(w):
        for j in range(h):
            print(nodes[i,j].type, end='\t')
        print()

def InitMap(w,h):
    global mapRow, mapCol, nodes, openlist, closelist
    mapRow = w
    mapCol = h
    for i in range(w):
        for j in range(h):
            nodes[i,j] = AStarNode()
            nodes[i, j].setPos(i, j)
 
'''
A* 算法本体
变量
openlist : 存放还没搜索到的节点。每次搜索都从中找出最优的节点进行拓展。当openlist为空时，说明所有可能的节点都搜索到了
closelist : 存放已经走过的节点，防止被再次搜索。
startnode : 用于临时存放每一次搜索的起点

算法运行
1.将当前起点加入closelist中 (如果是总的起点，令其 g = 0 , h = h。 f其实可以不用算了，因为不可能再被搜索到了)
2.拓展其子结点，判断是否能加入openlist中
    
3.将当前节点加入closelist
4.从openlist中取f最小的(最优)节点作为下一次搜索的起点startnode
5.判断程序是否应终止。终止条件:
    - openlist空了。说明所有节点都搜索过了
    - startnode = endnode。说明到终点了
'''
def FindPath(startRow,startCol,endRow,endCol):
    global mapRow,mapCol,nodes,openlist,closelist
    
    if startRow < 0 or startRow >= mapRow or startCol < 0 or startCol >= mapCol or endRow < 0 or endRow >= mapRow or endCol < 0 or endCol >= mapCol:
        print("开始或结束点在地图范围外！")
    
    startNode = nodes[startRow,startCol]
    endNode = nodes[endRow,endCol]  # 用于存放终点

    if startNode.type == 'stop' or endNode.type == 'stop':
        print("开始或结束点为障碍！")
        return
    
    openlist.clear()
    closelist.clear()

    # 把起点放入closelist
    closelist.append(startNode)

    while True:
        # 从当前起点开始，向4个方向拓展节点，并判断是否应该加入openlist
        # 参数 : 子结点(坐标), 子结点(坐标) , 需要的代价 ，父结点(起点) ， 终点(总的)
        FindNearlyToOpenList(startNode.row - 1, startNode.column, 1.0, startNode, endNode) # 上
        FindNearlyToOpenList(startNode.row, startNode.column - 1, 1.0, startNode, endNode) # 左
        FindNearlyToOpenList(startNode.row, startNode.column + 1, 1.0, startNode, endNode) # 右
        FindNearlyToOpenList(startNode.row + 1, startNode.column, 1.0, startNode, endNode) # 下
        #FindNearlyToOpenList(startNode.row - 1, startNode.column - 1, 1.4, startNode, endNode) 左上。朝对角线走的代价为sqrt(2)约为1.4
        #FindNearlyToOpenList(startNode.row - 1, startNode.column + 1, 1.4, startNode, endNode) 右上 
        #FindNearlyToOpenList(startNode.row + 1, startNode.column - 1, 1.4, startNode, endNode) 左下 
        #FindNearlyToOpenList(startNode.row + 1, startNode.column + 1, 1.4, startNode, endNode) 右下 

        ShowF()

        # 如果openlist为空了还未找到终点，则证明死路
        if len(openlist) == 0:
            print("死路一条！")
            return
        
        # 找到候选列表中f最小的点,作为下一次的搜索起点
        openlist = sorted(openlist,key=lambda x:x.f)  # 对整个列表升序排序，找到最小的
        closelist.append(openlist[0])
        startNode = openlist[0] # 更新下一次的搜索起点
        openlist.pop(0) 

        # 如果已经搜索到了终点,则得到最终路径
        if startNode == endNode:
            path = []   
            path.append(endNode)
            while endNode.father != None:
                path.append(endNode.father)
                endNode = endNode.father
            path.reverse()
            return path

'''
判断每个拓展出来的节点是否应该加入待搜索列表
参数 : 子结点坐标, 子结点坐标 , 需要的代价 ，父结点(起点) ， 终点(总的)
    noderow      nodecol       g       fathernode    endnode

程序运行
1.判读有没有出边界，是不是障碍物，有没有被搜索过
2.取当前层下的最优g值，用于计算f值
3.将其加入openlist
'''
def FindNearlyToOpenList(nodeRow,nodeCol,g,fatherNode,endNode):
    global mapRow,mapCol,nodes,openlist,closelist,findMethod
    # 边界判断
    if nodeRow < 0 or nodeRow >= mapRow or nodeCol < 0 or nodeCol >= mapCol:
        return
    node = nodes[nodeRow, nodeCol]
    # 判断其是否是障碍或者已经被搜索过了
    if (node == None) or (node.type == 'stop') or (node in closelist):
        return

    # 如果这个子结点也是待搜索的节点，而且它已经在同一层的搜索中产生过g值了，
    # 则应该计算新的g，与原来的g比较，取更小的。保证每一步都朝着离终点更近的地方搜索
    # 注意，这个节点不能视作“已经被搜索过的”！
    if node in openlist:
        newg = fatherNode.g + g
        if newg > node.g:
            return
        
    # 如果这个节点还没有放入openlist        
    # 找到父节点，通过到父节点时已经累积的代价和父节点到子结点的代价，计算起点到子结点的代价
    node.father = fatherNode
    node.g = fatherNode.g + g
    # h，默认用到终点的曼哈顿距离作为估算代价。
    if findMethod == "Manhattan":
        node.h = abs(endNode.row - node.row) + abs(endNode.column - node.column)
    elif findMethod == "Euclidean":
        node.h = ((endNode.row - node.row)**2 + (endNode.column - node.column)**2)**0.5

    # 计算子结点的f值
    node.f = node.g + node.h
    # 放入openlist
    openlist.append(node)

def CheckMap():
    global nodes
    checkStart = False
    checkEnd = False
    for bt in buttonNodes.values():
        if bt['bg'] == 'green':
            checkStart = True
        if bt['bg'] == 'red':
            checkEnd = True
    if checkEnd and checkStart:
        return True

def ShowF():
    global openlist, closelist,buttonNodes
    for node in openlist:
        buttonNodes[node.row, node.column]['text'] = str(round(node.f, 3))
    for node in closelist:
        buttonNodes[node.row, node.column]['text'] = str(round(node.f, 3))

def ChangeMethod(method,temp):
    global findMethod,methodButton1,methodButton2
    findMethod = method
    if temp == 1:
        methodButton1['bg'] = 'DeepPink'
        methodButton2['bg'] = '#6495ED'
    elif temp == 2:
        methodButton2['bg'] = 'DeepPink'
        methodButton1['bg'] = '#6495ED'

def ClearMap():
    global openlist, closelist, buttonNodes, nodes, mapRow, mapCol

    for btKey in buttonNodes.keys():
        buttonNodes[btKey]['bg'] = 'white'
        buttonNodes[btKey]['text'] = ''

    for i in range(mapRow):
        for j in range(mapCol):
            nodes[i,j] = AStarNode()
            nodes[i,j].setType('walk')
            nodes[i, j].setPos(i, j)

def MenuClick(i):
    global mapRow,mapCol,nodes,menuNode,buttonNodes,startRow,startCol,endRow,endCol,findMethod
    if i == 0 and CheckMap():
        menuNode = 0
        pathlist = FindPath(startRow, startCol, endRow, endCol)
        # 画出路径
        if pathlist is not None:
            for p in pathlist:
                if buttonNodes[p.row, p.column]['bg'] == 'white':
                    buttonNodes[p.row, p.column]['bg'] = 'Orange'
    elif i == 1:
        menuNode = 1
    elif i == 2:
        menuNode = 2
    elif i == 3:
        menuNode = 3
    elif i == 4:
        menuNode = 4
        ClearMap()

def CreateGUI():
    global mapRow,mapCol,nodes,buttonNodes,methodButton1,methodButton2
    
    window = tk.Tk()
    window.title('my window')
    window.geometry('1920x1027')

    tk.Button(window,text='开始',width=11,height=5,bg='#6495ED',command=lambda : MenuClick(i = 0)).grid(row=0,column=0,padx=0,pady=0)
    tk.Button(window,text='障碍',width=11,height=5,bg='#6495ED',command=lambda : MenuClick(i = 1)).grid(row=0,column=1,padx=0,pady=0)
    tk.Button(window,text='起点',width=11,height=5,bg='#6495ED',command=lambda : MenuClick(i = 2)).grid(row=0,column=2,padx=0,pady=0)
    tk.Button(window,text='终点',width=11,height=5,bg='#6495ED',command=lambda : MenuClick(i = 3)).grid(row=0,column=3,padx=0,pady=0)
    tk.Button(window,text='重置',width=11,height=5,bg='#6495ED',command=lambda : MenuClick(i = 4)).grid(row=0,column=4,padx=0,pady=0)
    methodButton1 = tk.Button(window, text='欧氏距离', width=11, height=5, bg='#6495ED', command=lambda: ChangeMethod(method="Euclidean", temp=1))
    methodButton1.grid(row=0, column=5, padx=0, pady=0)
    methodButton2 = tk.Button(window, text='曼哈顿距离', width=11, height=5, bg='DeepPink', command=lambda: ChangeMethod(method="Manhattan", temp=2))
    methodButton2.grid(row=0,column=6,padx=0,pady=0)
    for i in range(mapRow):
        for j in range(mapCol):
            buttonNodes[i,j] = tk.Button(window,text='',width=11,height=5,bg='white',command=lambda i=i,j=j: SetButton(i,j))
            buttonNodes[i,j].grid(row=1+i,column=j,padx=0,pady=0)

    window.mainloop()

def SetButton(i,j):
    global menuNode,buttonNodes,mapRow,mapCol,nodes,startRow,startCol,endRow,endCol
    if menuNode == -1:
        return
    elif menuNode == 1:
        if buttonNodes[i,j]['bg'] == 'black':
            nodes[i,j].type = 'walk'
            buttonNodes[i,j]['bg'] = 'white'
        else:
            nodes[i,j].type = 'stop'
            buttonNodes[i,j]['bg'] = 'black'
    elif menuNode == 2:
        for buttonKey,buttonValue in buttonNodes.items():
            if buttonValue['bg'] == 'green':
               buttonNodes[buttonKey]['bg'] = 'white'
               break
        buttonNodes[i,j]['bg'] = 'green'
        startRow,startCol = i,j
        nodes[i,j].type = 'walk'
    elif menuNode == 3:
        for buttonKey,buttonValue in buttonNodes.items():
            if buttonValue['bg'] == 'red':
               buttonNodes[buttonKey]['bg'] = 'white'
        buttonNodes[i,j]['bg'] = 'red'
        endRow,endCol = i,j
        nodes[i,j].type = 'walk'

InitMap(8, 17)
ShowNodes(8, 17)
print("_________________________________")
CreateGUI()