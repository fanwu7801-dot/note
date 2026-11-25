# 8-PyTorch与YOLOv5训练及数据标注

[总目录](总目录.md) · [上一篇：Python环境与基础](7-Python%E7%8E%AF%E5%A2%83%E4%B8%8E%E5%9F%BA%E7%A1%80.md) · [下一篇：RKNN模型转换与板端部署](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md)

[TOC]

<a id="part-12"></a>

## 8.1 安装PyTorch

打开命令行，输入

```shell
nvidia-smi
```

![image-20250428133352919](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428133352919.png)

 PyTorch官网下载链接：[Start Locally | PyTorch](https://pytorch.org/get-started/locally/)

![image-20250428133845804](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428133845804.png)

查看后面的下载命令的目标网址

```
https://download.pytorch.org/whl/cu121
```

![image-20250428133934494](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428133934494.png)

![image-20250428133957518](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428133957518.png)

![image-20250428134038774](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428134038774.png)

下面两条是 **Windows x86-64 / CPython 3.9 / CUDA 12.1** 的历史安装示例（wheel 中的 `cp39`、`win_amd64` 决定适用平台），不能用于前文 Linux/Python 3.10 的 RKNN 环境。实际安装从上方 PyTorch 官网按操作系统、Python、CPU/CUDA 组合选择兼容命令；RK 板载 NPU 不属于 CUDA 设备。

```shell
pip install E:\torch-2.1.0+cu121-cp39-cp39-win_amd64.whl
pip install E:\torchvision-0.16.0+cu121-cp39-cp39-win_amd64.whl
```

编译python程序测试：

```python
import torch
 
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
```

![image-20250428134207885](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428134207885.png)

<a id="part-13"></a>

> 环境准备见 [Python环境与基础](7-Python%E7%8E%AF%E5%A2%83%E4%B8%8E%E5%9F%BA%E7%A1%80.md#part-11) 和 [PyTorch安装与验证](8-PyTorch%E4%B8%8EYOLOv5%E8%AE%AD%E7%BB%83%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%87%E6%B3%A8.md#part-12)；本篇针对原仓库 YOLOv5 detect.py/train.py/export.py 工作流。


## 8.2 下载使用YoLo

**安装**：

```
# 如确需代理，再设置为你自己的可用代理地址。
sudo apt install git
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
# 先按当前系统安装兼容的 torch / torchvision，再安装 YOLOv5 依赖。
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**推理测试**：

```
# --source 0：摄像头；--weights：权重文件；--img：推理尺寸
python detect.py --source 0 --weights yolov5s.pt --img 640


```

**自定义训练**：

- 准备数据集（标注为YOLO格式的`.txt`文件）。

- 修改配置文件（如`data/coco.yaml`）。

- 运行训练命令：


```
# 安装 git
sudo apt install git

python train.py --img 640 --batch 16 --epochs 100 --data coco.yaml --weights yolov5s.pt

python train.py --data coco.yaml --epochs 100 --weights yolov5s.pt --cfg yolov5s.yaml --batch-size 8
```

> --img 640   指定图片大小
>
> --batch 16   一次算多少
>
> --epochs 100  算多轮
>
> --weights yolov5s.pt：指定用于初始化的权重文件；网络结构还需与权重和配置匹配。
>
> --data coco.yaml   指定数据集

**测试训练的模型**

> python detect.py --weights runs/train/exp/weights/best.pt --source img.jpg

`exp` 可能是 `exp2`、`exp3` 等，以本次训练输出目录为准。测试自训练模型应使用本次的 `best.pt`，不要仍加载官方预训练权重。

**模型转换**

使用以下命令将 `.pt` 模型转换为 `.onnx`：

```
python export.py --weights yolov5s.pt --include onnx --opset 12
```

关键参数说明：

- `--weights yolov5s.pt`：指定输入的 PyTorch 模型路径（可以是自定义模型或官方预训练模型，如 `yolov5s.pt`）。
- `--include onnx`：指定输出格式为 ONNX。
- `--opset 12`：选择 ONNX 算子集版本，应与目标 OpenCV/RKNN 转换器支持范围匹配，并完成导入测试；版本更高不代表兼容性更好。
- `--dynamic`（可选）：导出动态输入尺寸的模型（支持可变宽高）。
- `--simplify`（可选）：使用 `onnx-simplifier` 简化模型（减少冗余节点）。
- `--img-size 640`（可选）：指定输入图像的尺寸（默认 640x640）。

<a id="part-14"></a>

## 8.3 数据标注

> 影响推理准确度的因素：
>
> 1. 训练阶段
>    1. 数据标注不准确
>    2. 数据量太少
>    3. 训练数据和推理数据的差别太大
> 2. 推理阶段
>    1. 图片大小、像素、清晰度
>    2. 设置合适的置信度
>    3. 显示结果的时候调整相似度阈值

### 8.3.1 常见工具

#### 8.3.1.1 LabelImg

- **类型**：桌面应用（Windows/macOS/Linux）
- **格式支持**：YOLO（`.txt`）、PASCAL VOC（`.xml`）、CreateML（`.json`）
- **特点**：
  - 开源免费，界面简单，适合初学者。
  - 手动标注，支持矩形框（bounding box）。

------

#### 8.3.1.2 LabelMe

- **类型**：桌面/网页应用
- **格式支持**：JSON（需转换为YOLO格式）
- **特点**：
  
  - 支持多边形、矩形、圆形等多种标注，适合复杂形状。
  - 需要脚本转换JSON到YOLO格式（官方提供转换工具）。
- **安装**：

- ```
  pip install labelme
  labelme  # 启动后标注，保存为JSON
  ```

------

##### **3. CVAT（Computer Vision Annotation Tool）**

- **类型**：网页端（支持本地/服务器部署）
- **格式支持**：YOLO、COCO、VOC等
- **特点**：
  - 功能强大，支持团队协作、视频标注、自动标注（需配置模型）。
  - 适合大规模项目，但部署稍复杂。
- **安装**：

- ```
  docker-compose up -d  # 官方提供Docker部署
  ```

------

#### 8.3.1.3 Roboflow

- **类型**：在线平台（免费版有限制）
- **格式支持**：直接导出YOLOv5格式
- **特点**：
  - 自动化标注（AI辅助）、数据增强、版本管理。
  - 适合快速迭代，但需上传数据到云端。
- **网址**：[www.roboflow.com](https://www.roboflow.com)

------

#### 8.3.1.4 Makesense.ai

- **类型**：在线工具（无需安装）
- **格式支持**：YOLO、CSV等
- **特点**：
  - 完全免费，无需注册，适合轻量级标注。
  - 依赖浏览器，适合临时任务。
- **网址**：[www.makesense.ai](https://www.makesense.ai)

------

#### 8.3.1.5 VGG Image Annotator (VIA)

- **类型**：网页端/桌面端
- **格式支持**：JSON/CSV（需转换）
- **特点**：
  - 由牛津大学开发，支持多种标注类型。
  - 适合学术研究，但需手动转换格式。

------

#### 8.3.1.6 其他工具

- **Supervisely**：企业级平台，支持AI辅助标注。
- **RectLabel**：macOS专用，支持YOLO导出。
- **DarkLabel**：专注于视频标注，支持跟踪。

------

#### 8.3.1.7 标注后的关键步骤

1. **格式转换**：确保标注文件为YOLO格式（每张图对应一个`.txt`，内容为`class x_center y_center width height`，数值归一化到0-1）。
2. **目录结构**：

```
dataset/
  ├── images/
  │   ├── train/
  │   └── val/
  └── labels/
      ├── train/
      └── val/
 
 coco.yaml

coco.yaml:
train: /home/richard/dataset/images/train
val: /home/richard/dataset/images/val
nc: 2
names: ['yes', 'no']
```

**YOLOv5配置**：修改`data.yaml`文件，指定路径和类别。

**选择建议**

- **简单项目**：LabelImg或Makesense.ai。
- **复杂形状**：LabelMe或CVAT。
- **团队协作**：CVAT或Roboflow。
- **自动化需求**：Roboflow（AI辅助）或CVAT（集成模型）。

### 8.3.2 LabelImg的使用

1. 安装依赖：

```shell
pip install labelImg
sudo apt-get install pyqt5-dev-tools
pip install PyQt5  sip  lxml
```

```shell
win系统中
pip install labelimg
运行
labelimg
```

1. 运行

   ```shell
   labelImg
   ```

![image-20250428135124278](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428135124278.png)

4. 快捷键

   ![image-20250428135147901](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250428135147901.png)

5. 使用快捷键 “ Ctrl+U ” ， 选择图片存放目录 
6. 使用快捷键 “ Ctrl+R ” ，选择标定数据存放目录 
7. 设置格式
8. 按下键盘按键“W” ， 开始创建标注框。
9. 在弹出的窗口中命名目标识别内容的类别， 此处命名为“xxxx” 。 完成命名后，点击“OK” 按键， 或按下回车键“Enter” ， 保存此类别。
10. 使用快捷键“Ctrl+S” ， 保存当前图片的标注数据，
11. 接着使用按键“D” 跳转到下一张图片进行标注， 同样的步骤， 完成其他图片的标注操作即可。
12. 为了方便标注， 我们可以将软件上的自动保存的选项勾选上， 然后按照之前的标注步骤继续进行标注。

---

[总目录](总目录.md) · [上一篇：Python环境与基础](7-Python%E7%8E%AF%E5%A2%83%E4%B8%8E%E5%9F%BA%E7%A1%80.md) · [下一篇：RKNN模型转换与板端部署](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md)
