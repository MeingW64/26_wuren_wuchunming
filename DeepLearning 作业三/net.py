import torch
from torch import nn
from torchvision import transforms, datasets
from torch.utils.data.dataloader import DataLoader
import torch.optim as optim
import torch.nn.functional as F
from torchinfo import summary
import os
import glob

class mixed_net(nn.Module):
    def __init__(self):
        super(mixed_net, self).__init__()

        # 主要采用两个卷积层，两个最大池化层和一个全局平均池化层，最后接三个全连接层

        # 1.卷积层  5×5卷积核，输入3通道(RGB)，输出16通道的特征
        # padding = 1 保持输入输出尺寸不变
        # 3 * 64 * 64 -> 16 * 64 * 64
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)

        # 2.归一化层。将下一层的输入标准化为均值为0，方差为1的分布
        # 能够提升模型稳定性，让我们能用更大的学习率，加快收敛。甚至还有正则化的作用，减少过拟合
        # 16 * 64 * 64 -> 16 * 64 * 64
        self.bn1 = nn.BatchNorm2d(16)

        # 使用relu激活函数

        # 3.池化层 使用2×2的最大池化，步长为2。将特征图尺寸减半，降低计算量
        # 16 * 64 * 64 -> 16 * 32 * 32      
        self.pool1 = nn.MaxPool2d(2)

        # 4.卷积层  3×3卷积核，输入16通道，输出32通道的特征
        # 16 * 32 * 32 -> 32 * 32 * 32
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        
        # 5.归一化层
        # 32 * 32 * 32 -> 32 * 32 * 32
        self.bn2 = nn.BatchNorm2d(32)

        # 6.池化层 使用2×2的最大池化，步长为2。将特征图尺寸减半，降低计算量
        # 32 * 32 * 32 -> 32 * 16 * 16
        self.pool2 = nn.MaxPool2d(2)

        # 7.全局池化层。将每个通道的特征图压缩成一个数，得到一个长度为32的特征向量
        # 完全舍弃对应颜色的空间信息，只保留颜色特征，大大减少参数量
        # 32 * 16 * 16 -> 32 * 1 * 1
        self.gap = nn.AdaptiveAvgPool2d(1)

        
        # 8.全连接层 32 -> 64
        self.fc1 = nn.Linear(32, 64)

        # 9.全连接层 64 -> 32
        self.fc2 = nn.Linear(64, 32)

        # 10.全连接层 32 -> 3。最后只输出三种颜色的概率
        self.fc3 = nn.Linear(32, 3)

        # self.dropout = nn.Dropout(0.05) # 随机丢弃5%的神经元，减少过拟合
        # byd我都欠拟合了

    def forward(self, x):
        '''
        公式： W = (W + 2padding - kernel_w) / stride + 1

        '''
        # 输入: 3 * 64 * 64
        x = self.conv1(x)          # 16 * 64 * 64
        x = self.bn1(x)            
        x = F.relu(x)              # 使用relu激活函数
        x = self.pool1(x)          # 16 * 32 * 32

        x = self.conv2(x)          # 32 * 32 * 32
        x = self.bn2(x)            
        x = F.relu(x)              
        x = self.pool2(x)          # 32 * 16 * 16

        x = self.gap(x)            # 32 * 1 * 1
        x = x.view(x.size(0), -1)  # 32

        x = self.fc1(x)            # 64
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)            # 32
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)            # 3
        return x

def evaluate(model, test_loader, device):
    '''
    验证模型
    '''
    model.eval()
    class_correct = [0, 0, 0]
    class_total = [0, 0, 0]

    with torch.no_grad():  # 不需要计算梯度，节约算力
        for datas, labels in test_loader:    # 遍历每一个标签对应的数据
            datas, labels = datas.to(device), labels.to(device)
            outputs = model(datas)  # 计算对应标签下数据在模型上的输出
            _, predicted = torch.max(outputs, dim=1) # 取三种颜色中概率最大的 predicted = [0 , 1, 2 ...]

            matches = (predicted == labels)  # 所有与原标签符合的
            for i in range(len(labels)):
                label = labels[i].item()  # 张量化为标量
                class_correct[label] += matches[i].item()  # 统计每个标签下正确的数量
                class_total[label] += 1 

    overall = 100.0 * sum(class_correct) / sum(class_total)
    per_class = [100.0 * class_correct[i] / class_total[i] for i in range(3)] # 每个标签的正确率
    return overall, per_class



if __name__ == "__main__":
    #设置超参数
    BATCH_SIZE = 1024         
    EPOCH = 150             
    LEARNING_RATE = 0.005    # 初始学习率定为0.01

    # 将设备选定为独显。后续数据可以用to(device)直接放到显卡上
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"使用设备: {device}")

    # 对训练数据集进行增强
    train_transform = transforms.Compose([
        transforms.Resize([64, 64]),
        transforms.RandomHorizontalFlip(p=0.3),   # 将30%的图像水平翻转
        transforms.RandomRotation(10),         # 将图像随机旋转±10度
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),  # 随机调整亮度、对比度和饱和度
        transforms.ToTensor(),  # 将图像转换为张量
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # 将图像张量标准化
    ])
    # 对于测试集，不用加强
    test_transform = transforms.Compose([
        transforms.Resize([64, 64]),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # 加载数据集
    trainset = datasets.ImageFolder(root=r'dataset/train',transform=train_transform)
    testset1 = datasets.ImageFolder(root=r'dataset/test1',transform=test_transform)
    testset2 = datasets.ImageFolder(root=r'dataset/test2',transform=test_transform)

    print(f"训练集图片数量: {len(trainset)}")
    print(f"测试集1图片数量: {len(testset1)}")
    print(f"测试集2图片数量: {len(testset2)}")
    print(f"标签映射: {trainset.class_to_idx}")

    train_loader = DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True,pin_memory=True, num_workers=0)
    test_loader1 = DataLoader(testset1, batch_size=BATCH_SIZE, shuffle=False,pin_memory=True, num_workers=0)
    test_loader2 = DataLoader(testset2, batch_size=BATCH_SIZE, shuffle=False,pin_memory=True, num_workers=0)

    # 创建网络
    net = mixed_net().to(device)
    summary(net, input_size=(1, 3, 64, 64), device=device)
    print(f'标签对应的ID: {trainset.class_to_idx}')

    # 设置损失函数，优化器。
    criterion = nn.CrossEntropyLoss()  # 使用交叉熵损失函数，收敛比误差平方和更快
    optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE , weight_decay=1e-4)   # 使用Adam优化器
    #optimizer =optim.SGD(net.parameters(), lr=LEARNING_RATE, momentum=0.9)

    # 使用余弦退火来调节学习率。以30轮训练为一个周期，周期内学习率从初始值逐渐降低到1e-5，然后重新回升到初始值，周期长度翻倍
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=30, T_mult=2, eta_min=1e-5)  

    os.makedirs("pth", exist_ok=True)
    acc_max = 0.0   # 最佳准确率
    best_epoch = 0   # 最佳训练轮数

    print("Start")

    # 模型的训练迭代过程
    for epoch in range(EPOCH):
        net.train()
        train_loss = 0.0

        for batch_id, (datas, labels) in enumerate(train_loader):
            datas, labels = datas.to(device), labels.to(device)  # 将所有数据放到显卡上加速运算

            optimizer.zero_grad()  # 清空之前的梯度
            outputs = net(datas)  # 连接所有层得到输出结果
            loss = criterion(outputs, labels) # 计算交叉熵损失
            loss.backward()  # 反向传播计算梯度
            optimizer.step()  # 更新模型参数

            train_loss += loss.item() * datas.size(0) # 累加每个批次的损失总和

        avg_loss = train_loss / len(trainset)   # 计算平均损失
        scheduler.step()   # 更新学习率
        lr = scheduler.get_last_lr()[0]

        # 验证
        acc1, per_class1 = evaluate(net, test_loader1, device)
        acc2, per_class2 = evaluate(net, test_loader2, device)
        acc3, per_class3 = evaluate(net, train_loader, device)  # 综合评估模型的表现
        acc_ave = (acc1 + acc2 + acc3) / 3
        print(f"Epoch {epoch+1:3d}/{EPOCH} | Loss: {avg_loss:.4f} | LR: {lr:.6f}")
        print(f"    Test1: {acc1:.2f}% | 蓝:{per_class1[0]:.1f}% 红:{per_class1[1]:.1f}% 黄:{per_class1[2]:.1f}%")
        print(f"    Test2: {acc2:.2f}% | 蓝:{per_class2[0]:.1f}% 红:{per_class2[1]:.1f}% 黄:{per_class2[2]:.1f}%")
        print(f"    Train: {acc3:.2f}% | 蓝:{per_class3[0]:.1f}% 红:{per_class3[1]:.1f}% 黄:{per_class3[2]:.1f}%")

        # 保存最佳模型（以 test1 准确率为准）
        if acc_ave > acc_max:
            acc_max = acc_ave
            best_epoch = epoch + 1
            # 删除旧的 best 模型
            for old in glob.glob("pth/model_best_*.pth"):
                os.remove(old)
            save_path = f"pth/model_best.pth"
            torch.save(net.state_dict(), save_path)
            print(f"保存最佳模型: {save_path}")

    print(f"最佳平均准确率: {acc_max:.2f}% (第 {best_epoch} 轮)")