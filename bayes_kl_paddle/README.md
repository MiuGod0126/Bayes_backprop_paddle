# Bayes by Backprop    
[TOC]

## 一、简介

[Weight Uncertainty in Neural Networks](https://arxiv.org/pdf/1505.05424.pdf)

  传统的神经网络学习的权重w是个固定的值，而本文的贝叶斯神经网络学习的是权重的分布。该网络在推理时用蒙特卡罗法采样，生成多个不同的权重,然后对相同输入推理为不同概率分布，然后再取平均，相当于起到了集成模型的作用，本文认为潜在不确定性的权重能够提升网络的泛化能力。

​	本项目还原的是kumar-shridhar的repo，由于损失函数中kl用的是高斯的kl散度，故名为bayes_kl_paddle。

## 二、复现精度
 MNIST测试集上，Test Error=1.3183%
## 三、数据集
MNIST手写数字数据集，共有6w训练集、1w测试集，像素为32。本项目从训练集划出1w做为验证集，用于选择模型，并把所有像素除126作为预处理。
## 四、环境依赖
- 硬件：
  - Aistudio 至尊版本 V100（mnist28 bbb）/ 3060(mnist28lrt，mnist32 bbb)
- 框架
  - PaddlePaddle >=2.0.0

## 五、快速开始

### 5.1训练

```
python main.py --config ./config/base.yaml --mode train
```

### 5.2 评估

```
python main.py  --config ./config/base.yaml --mode eval
```

### 5.3 预测

```
python main.py  --config ./config/base.yaml --mode pred
```

## 六、代码结构与详细说明

### 6.1 目录结构

```
.
├── README_cn.md
├── checkpoints # 模型权重
├── config # 配置文件
├── data # 数据加载
├── eval.py # 评估脚本
├── image # 指标图片
├── logs # 日志
├── main.py # 主函数，负责训练、评估、预测
├── model
│   ├── xxxNet.py  # 贝叶斯神经网络
│   └── layers
│       ├── BBB # 贝叶斯linear、conv算子
│       ├── BBB_LRT # 带有局部重参数化trick的贝叶斯linear、conv算子
│       └── misc.py #贝叶斯模型基类
├── predict.py # 预测脚本
├── train.py # 训练脚本
└── utils # 日志、指标等工具

```

### 6.2 参数说明

```
############### Configuration file for Bayesian ###############
data:
  name: MNIST # 'MNIST','CIFAR10','CIFAR100' # 数据集名
  input_size: [1,32,32] # 数据集大小
  # 归一化
  mean: [0.]
  std: [126.]
  class_dim: 10 #类别数
  valid_size: 10000 #验证集大小，如果是0-1间小数则按比例取，如果是整数则取valid_size个验证集
  num_workers: 0 # 加载数据的线程数

hparas:
  seeds: 2021 # 随机种子
  start_epoch: 0 # 开始训练轮数
  num_epochs: 500 # 总训练轮数
  batch_size: 128 # batch大小
  learning_strategy:
    lr_start: 1e-3 # 初始学习率        
    lr_decay: 0.8 # 学习率衰减比
    weight_decay: 0.015 #权重衰减
  visual_epochs: 50 # 画图间隔
  save_epochs: 50 #保存模型间隔

model:
  name: 2fc # [lenet,alex,3conv3fc,2fc] 模型名
  layer_type: bbb  # 'bbb' or 'lrt' # 层类型，贝叶斯反向传播、或带有局部重参数化trick的bayes层
  load_name: model_best_lrt.pdparams # model_best_bbb,model_best_lrt #加载训练好的模型
  activation_type: relu  # 'softplus' or 'relu' # 激活函数
  beta_type: Blundell # 'Blundell', 'Standard',或常量 （Blundell是论文里对mini-batch的加权法）
  train_ens: 1 # 训练时模型集成数
  valid_ens: 5 # 验证时模型集成数
  priors: # 先验+后验
    # prior
    prior_mu:   0
    prior_sigma: 0.1
    # gaussian posterior
    posterior_mu_initial: [0, 0.1]  # (mean, std) normal_
    posterior_rho_initial: [-5, 0.1] # (mean, std) normal_
  save_dir: "checkpoints" # 保存模型目录
```

## 七、模型信息

### 7.1 相关信息

| 数据集 | 模型                          | Test-error | 权重链接                                                     |
| ------ | ----------------------------- | ---------- | ------------------------------------------------------------ |
| MNIST32 | bayesfc2-bbb(1200units/layer) | 1.3183% | [链接:](https://pan.baidu.com/s/1luZ0ndOsPRJ0Xxcoe0F8aw)  提取码: yv6b |
| MNIST28 | bayesfc2-bbb(1200units/layer) | 1.3183% | [链接:](https://pan.baidu.com/s/1z_SIme8HOhrxqctBbJ-S1w)  提取码: opq3 |
| MNIST28 | bayesfc2-lrt(1200units/layer) | 1.3183%     | 同上                                                         |

注：mnist28中用lrt加载bbb的权重能达到1.289%,而mnist32的是第250轮保存的权重

