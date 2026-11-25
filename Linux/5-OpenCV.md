# 5-OpenCV

[总目录](总目录.md) · [上一篇：RK开发板入门与交叉编译及NFS](4-RK%E5%BC%80%E5%8F%91%E6%9D%BF%E5%85%A5%E9%97%A8%E4%B8%8E%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%8F%8ANFS.md) · [下一篇：人工智能与边缘计算基础](6-%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E4%B8%8E%E8%BE%B9%E7%BC%98%E8%AE%A1%E7%AE%97%E5%9F%BA%E7%A1%80.md)

[TOC]

<a id="part-9"></a>

> 本篇完整保留 OpenCV 的理论、API 与实验；YOLOv5 后处理示例已按其明确的 ONNX 输出约定修正。


## 5.1 介绍

OpenCV 是一个功能强大、应用广泛的计算机视觉库，它为开发人员提供了丰富的工具和算法，可以帮助他们快速构建各种视觉应用。

随着计算机视觉技术的不断发展，OpenCV 也将会继续发挥重要的作用。

OpenCV 提供了大量的计算机视觉算法和图像处理工具，广泛应用于图像和视频的处理、分析以及机器学习领域。

![img](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/0_NaLPVSCOjjSh0oxJ.jpg)

### 5.1.1 OpenCV 核心特点

1. **开源与免费**
   OpenCV 是一个开源项目，任何人都可以免费使用、修改和分发其代码。这意味着你可以根据需要对 OpenCV 进行定制化修改。
2. **跨平台支持**
   OpenCV 支持多个操作系统平台，包括 Windows、Linux、macOS、Android 和 iOS。你可以在各种设备上使用 OpenCV，包括桌面、服务器以及移动设备。
3. **支持多种编程语言**
   OpenCV 提供了多种编程语言的接口，支持 C++、Python、Java、JavaScript 和 MATLAB 等多种编程语言。因此，无论你是 C++ 开发者还是 Python 爱好者，都能轻松使用 OpenCV。
4. **强大的功能库**
   OpenCV 提供了数百个优化的算法，涵盖了计算机视觉和图像处理的方方面面。以下是一些常见的应用：
   - **图像处理：** 图像滤波、边缘检测、颜色空间转换、形态学操作、特征提取等。
   - **视频分析：** 视频捕捉、运动分析、物体检测与追踪等。
   - **机器学习与人工智能：** OpenCV 集成了深度学习框架，可以进行人脸识别、目标检测、图像分类等。
   - **计算机视觉：** 图像匹配、物体识别、立体视觉、深度图计算等。
5. **高效的性能**
   OpenCV 内置的许多算法都经过高度优化，支持硬件加速（如 Intel 的 TBB、OpenCL、CUDA 等技术），使得它在处理复杂计算时具备高性能，尤其在处理视频流和实时图像分析时非常高效。

### 5.1.2 OpenCV 的应用领域

OpenCV 的应用领域非常广泛，涵盖了计算机视觉的各个方面，例如：

- **图像处理:** 图像滤波、图像增强、图像分割、图像特征提取等。
- **视频分析:** 目标跟踪、运动检测、行为识别等。
- **物体识别:** 人脸识别、车牌识别、物体识别等。
- **机器学习:** 支持向量机、K 均值聚类、神经网络等。
- **深度学习:** 图像分类、目标检测、图像分割等。
- **增强现实:** 虚拟物体叠加、手势识别等。
- **机器人:** 视觉导航、目标抓取等。

**应用场景**

- **人脸识别与检测：** 利用图像中人脸的特征进行身份验证，应用于安全系统、社交媒体和照片管理等领域。
- **物体检测与跟踪：** 在监控、无人驾驶、工业检测等场景中，通过检测和跟踪目标物体来进行分析。
- **增强现实（AR）：** 将虚拟信息叠加到现实世界的图像中，广泛应用于游戏、医疗、工业等领域。
- **医疗图像分析：** 使用 OpenCV 分析医学图像（如 CT 扫描、MRI 图像）来帮助诊断疾病。
- **机器人视觉：** 机器人通过视觉识别环境，进行物体操作、导航等任务。
- **无人驾驶：** 在自动驾驶中，OpenCV 被用于车道检测、交通标志识别、障碍物检测等任务。

![img](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/10b73475-8e3f-42e9-beb6-ecb880612835-20250425085609817.webp)

**OpenCV 的未来发展**

随着人工智能和计算机视觉技术的快速发展，OpenCV 也在不断更新和完善。未来，OpenCV 将会在以下几个方面继续发展：

- **深度学习:** 进一步加强对深度学习的支持，提供更多的预训练模型和算法。
- **移动端:** 优化 OpenCV 在移动端的性能，使其更适合移动应用开发。
- **云计算:** 提供基于云计算的计算机视觉服务，方便用户进行大规模图像和视频处理。

## 5.2 安装

OpenCV（Open Source Computer Vision Library）是一个开源的计算机视觉和机器学习软件库，包含了数百个计算机视觉算法，广泛应用于图像处理、视频分析、物体检测、人脸识别等领域。

C++ 是 OpenCV 的原始开发语言，适合高性能应用。

在 C++ 项目中使用 OpenCV 之前，首先需要安装 OpenCV 库。

**下载 OpenCV**

访问 OpenCV 的官方下载页面：https://opencv.org/releases/。

选择适合你操作系统的版本（例如 Windows、Linux、macOS）并下载，例如OpenCV 4.x 的 Windows 预编译包。

> apt安装
>
> sudo apt install libopencv-dev

**Linux**

我们可以从 OpenCV 的 [GitHub 仓库](https://github.com/opencv/opencv) 下载源码，或者直接从 OpenCV 的 [官方网站](https://opencv.org/releases/) 下载预编译的版本。

使用 Git 克隆源码：

```
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git  # 可选，包含额外的模块
```

**使用 CMake 配置 OpenCV**

1、创建一个构建目录并进入：

```
sudo apt install libgtk2.0-dev pkg-config -y
mkdir build
cd build
```

2、使用 CMake 生成构建文件：

```
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..
//执行cmake时会下载一个文件，比较慢，可以使用vpn提升速度
export http_proxy=ip:端口
export https_proxy=ip:端口
```

如果你需要额外的模块（如 `opencv_contrib`），可以添加以下参数：

```
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules ..
```

3、编译并安装 OpenCV：

```
make -j4  # 使用 4 个线程进行编译
sudo make install
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

### 5.2.1 Helloworld

```c++
#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    // 读取图片
    cv::Mat image = cv::imread("example.jpg");

    // 检查图片是否成功加载
    if (image.empty()) {
        std::cout << "无法加载图片！" << std::endl;
        return -1;
    }

    // 显示图片
    cv::imshow("Display Image", image);

    // 等待按键
    cv::waitKey(0);

    return 0;
}
```

```c
# 配置cmake的最低版本
cmake_minimum_required(VERSION 3.10)
# 配置项目名称和使用的语言
project(MyProject CXX)

# 自动搜索并配置项目的依赖库open
find_package(OpenCV REQUIRED)

# 配置项目的源文件
set(Project_SRC
    main.cpp
)

# 配置项目的源语言件
add_executable(MyProject ${Project_SRC})

# 链接依赖库
target_link_libraries(MyProject ${OpenCV_LIBS})

# 配置项目安装路径的相对位置
set(CMAKE_INSTALL_PREFIX "../")
# 配置项目的安装路径
install(TARGETS MyProject RUNTIME DESTINATION install)

```

## 5.3 基础操作

**官方API文档**

> https://docs.opencv.org/3.4.5/index.html

### 5.3.1 图像的基本操作

#### 5.3.1.1 读取、显示和保存图像

在 OpenCV 中，图像的基本操作包括读取、显示和保存图像。这些操作是图像处理的基础。

**读取图像**：使用`imread`函数读取图像。该函数的第一个参数是图像文件的路径，第二个参数是读取图像的方式（如彩色图像、灰度图像等）。

```
cv::Mat image = cv::imread("image.jpg", cv::IMREAD_COLOR);
```

**显示图像**：使用`imshow`函数显示图像。该函数的第一个参数是窗口的名称，第二个参数是要显示的图像。

```
cv::imshow("Display Window", image);
cv::waitKey(0); // 等待按键按下
```

**保存图像**：使用`imwrite`函数保存图像。该函数的第一个参数是保存文件的路径，第二个参数是要保存的图像。

```
cv::imwrite("output.jpg", image);
```

#### 5.3.1.2 图像的基本属性

图像的基本属性包括尺寸、通道数和像素值。

**尺寸**：图像的尺寸可以通过`rows`和`cols`属性获取。

```
int height = image.rows;
int width = image.cols;
```

**通道数**：图像的通道数可以通过`channels()`方法获取。

```
int channels = image.channels();
```

**像素值**：可以通过`at`方法访问图像的像素值。

```
cv::Vec3b pixel = image.at<cv::Vec3b>(y, x); // 访问(x, y)处的像素值
```

#### 5.3.1.3 图像的创建与初始化

可以通过`Mat`类创建和初始化图像。

**创建图像**：可以创建一个指定大小和类型的图像。

```
cv::Mat newImage(480, 640, CV_8UC3, cv::Scalar(0, 0, 255)); // 创建一个640x480的红色图像
```

**初始化图像**：可以使用`setTo`方法初始化图像。

```
image.setTo(cv::Scalar(255, 255, 255)); // 将图像初始化为白色
```

#### 5.3.1.4 图像的像素操作

图像的像素操作包括遍历像素和修改像素值。

**遍历像素**：可以使用双重循环遍历图像的每个像素。

```
for (int y = 0; y < image.rows; y++) {
    for (int x = 0; x < image.cols; x++) {
        cv::Vec3b& pixel = image.at<cv::Vec3b>(y, x);
        // 对像素进行操作
    }
}
```

**修改像素值**：可以直接修改像素的值。

```
pixel[0] = 255; // 将蓝色通道设置为255
pixel[1] = 0;   // 将绿色通道设置为0
pixel[2] = 0;   // 将红色通道设置为0
```

### 5.3.2 几何图形的绘制

**线条**

```c++
cv::line(image, cv::Point(0, 0), cv::Point(480, 480), cv::Scalar(0, 0, 255), 2);
```

**矩形**

```c++
    /**
     * 画矩形
     * cv::rectangle(image, 左上角坐标, 右下角坐标, 颜色, 线宽)
     */
    cv::rectangle(image, cv::Point(300, 100), cv::Point(400, 300), cv::Scalar(0, 255, 255), 2);

    /**
     * 画矩形
     * cv::rectangle(image, 矩形, 颜色, 线宽)
     */
    cv::rectangle(image, cv::Rect(50,100,50,100), cv::Scalar(255, 0, 0), 2);
```

**文字**

```c++
    /**
     * 写字
     * cv::putText(image, 文字, 坐标, 字体, 大小, 颜色, 线宽)
     */
    cv::putText(image, "OpenCV", cv::Point(50, 50), cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 0, 255), 2);
```

### 5.3.3 图像的几何变换

#### 5.3.3.1 缩放、旋转、平移、翻转

图像的几何变换包括缩放、旋转、平移和翻转。

**缩放**：使用`resize`函数缩放图像。

```
cv::Mat resizedImage;
cv::resize(image, resizedImage, cv::Size(newWidth, newHeight));
```

**旋转**：使用`getRotationMatrix2D`和`warpAffine`函数旋转图像。

```
cv::Point2f center(image.cols / 2.0, image.rows / 2.0);
cv::Mat rotationMatrix = cv::getRotationMatrix2D(center, angle, 1.0);
cv::Mat rotatedImage;
cv::warpAffine(image, rotatedImage, rotationMatrix, image.size());
```

**平移**：使用`warpAffine`函数平移图像。

```
cv::Mat translationMatrix = (cv::Mat_<double>(2, 3) << 1, 0, tx, 0, 1, ty);
cv::Mat translatedImage;
cv::warpAffine(image, translatedImage, translationMatrix, image.size());
```

**翻转**：使用`flip`函数翻转图像。

```
cv::Mat flippedImage;
cv::flip(image, flippedImage, 1); // 1表示水平翻转，0表示垂直翻转
```

#### 5.3.3.2 仿射变换与透视变换

**仿射变换**：仿射变换是线性变换加上平移，可以使用`warpAffine`函数实现。

```
cv::Mat affineMatrix = cv::getAffineTransform(srcPoints, dstPoints);
cv::Mat affineImage;
cv::warpAffine(image, affineImage, affineMatrix, image.size());
```

**透视变换**：透视变换是更一般的变换，可以使用`warpPerspective`函数实现。

```
cv::Mat perspectiveMatrix = cv::getPerspectiveTransform(srcPoints, dstPoints);
cv::Mat perspectiveImage;
cv::warpPerspective(image, perspectiveImage, perspectiveMatrix, image.size());
```

------

### 5.3.4 图像的颜色空间转换

#### 5.3.4.1 RGB、灰度、HSV等颜色空间

图像的颜色空间包括RGB、灰度和HSV等。

- **RGB**：RGB是最常见的颜色空间，表示红、绿、蓝三个通道。
- **灰度**：灰度图像只有一个通道，表示亮度。
- **HSV**：HSV颜色空间表示色调（Hue）、饱和度（Saturation）和亮度（Value）。

#### 5.3.4.2 颜色空间转换

使用 `cvtColor` 函数进行颜色空间转换。

**BGR 转RGB**：

```c++
cv::Mat rgbImage;
cv::cvtColor(image, grayImage, cv::COLOR_BGR2RGB);
```

**BGR 转灰度**：

```
cv::Mat grayImage;
cv::cvtColor(image, grayImage, cv::COLOR_BGR2GRAY);
```

**RGB转HSV**：

```
cv::Mat hsvImage;
cv::cvtColor(image, hsvImage, cv::COLOR_BGR2HSV);
```

**二值化**

```c++
int threshold_value = 127;
cv::Mat target;
//二值化  threshold阈值
cv::threshold(dst, target, threshold_value, 255, cv::THRESH_BINARY);
```

#### 5.3.4.3 通道分离与合并

**通道分离**：使用`split`函数将图像的通道分离。

```
std::vector<cv::Mat> channels;
cv::split(image, channels);
```

**通道合并**：使用`merge`函数将多个通道合并为一个图像。

```
cv::Mat mergedImage;
cv::merge(channels, mergedImage);
```

------

### 5.3.5 实验

C++ OpenCV 的基础操作包括图像的读取、显示、保存、像素操作、图像属性获取等。

以下是一些常见的 OpenCV 基础操作及其代码示例：

#### 5.3.5.1 图像的读取与显示

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   // 检查图像是否成功加载
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 显示图像
   namedWindow("Display Image", WINDOW_AUTOSIZE);
   imshow("Display Image", image);
 
   // 等待按键
   waitKey(0);
 
   // 关闭窗口
   destroyAllWindows();
 
   return 0;
 }
```

#### 5.3.5.2 图像的保存

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 保存图像
   bool isSaved = imwrite("saved_image.jpg", image);
   if (isSaved) {
     cout << "图像保存成功！" << endl;
   } else {
     cout << "图像保存失败！" << endl;
   }
 
   return 0;
 }
```

#### 5.3.5.3 获取图像属性

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 获取图像属性
   int width = image.cols;  // 图像宽度
   int height = image.rows; // 图像高度
   int channels = image.channels(); // 图像通道数
 
   cout << "图像宽度: " << width << endl;
   cout << "图像高度: " << height << endl;
   cout << "图像通道数: " << channels << endl;
 
   return 0;
 }
```

#### 5.3.5.4 访问和修改像素值

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 访问像素值（BGR格式）
   Vec3b pixel = image.at<Vec3b>(100, 100); // 获取(100, 100)位置的像素值
   cout << "B: " << (int)pixel[0] << ", G: " << (int)pixel[1] << ", R: " << (int)pixel[2] << endl;
 
   // 修改像素值
   image.at<Vec3b>(100, 100) = Vec3b(255, 0, 0); // 将(100, 100)位置的像素设置为蓝色
 
   // 显示修改后的图像
   imshow("Modified Image", image);
   waitKey(0);
   destroyAllWindows();
 
   return 0;
 }
```

#### 5.3.5.5 图像颜色空间转换

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 转换为灰度图像
   Mat grayImage;
   cvtColor(image, grayImage, COLOR_BGR2GRAY);
 
   // 显示灰度图像
   imshow("Gray Image", grayImage);
   waitKey(0);
   destroyAllWindows();
 
   return 0;
 }
```

#### 5.3.5.6 图像的裁剪与缩放

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 裁剪图像
   Rect roi(100, 100, 200, 200); // (x, y, width, height)
   Mat croppedImage = image(roi);
 
   // 缩放图像
   Mat resizedImage;
   resize(image, resizedImage, Size(400, 400)); // 缩放到400x400
 
   // 显示裁剪和缩放后的图像
   imshow("Cropped Image", croppedImage);
   imshow("Resized Image", resizedImage);
   waitKey(0);
   destroyAllWindows();
 
   return 0;
 }
```

#### 5.3.5.7 图像的复制与克隆

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 复制图像
   Mat copiedImage = image.clone();
 
   // 修改复制的图像
   circle(copiedImage, Point(100, 100), 50, Scalar(0, 255, 0), 2); // 在复制的图像上画一个圆
 
   // 显示原始图像和修改后的图像
   imshow("Original Image", image);
   imshow("Copied Image", copiedImage);
   waitKey(0);
   destroyAllWindows();
 
   return 0;
 }
```

#### 5.3.5.8 图像的几何变换

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
 
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 旋转图像
   Mat rotatedImage;
   Point2f center(image.cols / 2, image.rows / 2); // 旋转中心
   double angle = 45; // 旋转角度
   double scale = 1.0; // 缩放比例
   Mat rotationMatrix = getRotationMatrix2D(center, angle, scale);
   warpAffine(image, rotatedImage, rotationMatrix, image.size());
 
   // 显示旋转后的图像
   imshow("Rotated Image", rotatedImage);
   waitKey(0);
   destroyAllWindows();
 
   return 0;
 }
```

## 5.4 模块

OpenCV 是一个功能强大的计算机视觉库，包含多个模块，每个模块专注于不同的任务。

以下是 OpenCV 中一些核心模块：

| **模块名称**    | **主要功能**                                                 | **常用类/函数**                                              |
| --------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Core**        | 提供基本数据结构和函数，如图像存储、矩阵操作、文件 I/O 等。  | `Mat`, `Point`, `Size`, `Rect`, `Scalar`, `FileStorage`, `cv::format` |
| **Imgproc**     | 图像处理功能，包括滤波、几何变换、颜色空间转换、边缘检测、形态学操作、阈值化等。 | `cvtColor`, `GaussianBlur`, `Canny`, `threshold`, `resize`, `warpAffine` |
| **Highgui**     | 图像和视频的显示、窗口管理、用户交互（如鼠标事件、滑动条）。 | `imshow`, `namedWindow`, `waitKey`, `createTrackbar`, `setMouseCallback` |
| **Video**       | 视频处理功能，包括视频捕获、背景减除、光流计算等。           | `VideoCapture`, `VideoWriter`, `BackgroundSubtractor`, `calcOpticalFlowPyrLK` |
| **Calib3d**     | 相机标定、3D 重建、姿态估计等。                              | `findChessboardCorners`, `calibrateCamera`, `solvePnP`, `recoverPose` |
| **Features2d**  | 特征检测与描述，包括关键点检测、特征匹配等。                 | `ORB`, `SIFT`, `SURF`, `BFMatcher`, `FlannBasedMatcher`      |
| **Objdetect**   | 目标检测功能，如 Haar 级联检测、HOG 检测等。                 | `CascadeClassifier`, `HOGDescriptor`                         |
| **DNN**         | 深度学习模型的加载和推理，支持 TensorFlow、PyTorch、Caffe 等框架。 | `readNet`, `blobFromImage`, `Net::forward`                   |
| **ML**          | 机器学习算法，如 KNN、SVM、决策树等。                        | `KNearest`, `SVM`, `DTrees`, `TrainData`                     |
| **Flann**       | 快速近似最近邻搜索（FLANN），用于特征匹配和高维数据搜索。    | `Index`, `KDTreeIndexParams`, `SearchParams`                 |
| **Photo**       | 图像修复、去噪、HDR 成像等。                                 | `inpaint`, `fastNlMeansDenoising`, `createTonemap`           |
| **Stitching**   | 图像拼接功能，用于创建全景图。                               | `Stitcher`, `Stitcher::create`                               |
| **Shape**       | 形状分析和匹配。                                             | `ShapeDistanceExtractor`, `ShapeContextDistanceExtractor`    |
| **Tracking**    | 目标跟踪算法，如 MIL、KCF、GOTURN 等。                       | `TrackerMIL`, `TrackerKCF`, `TrackerGOTURN`                  |
| **Videoio**     | 视频输入输出功能，支持多种视频格式和摄像头。                 | `VideoCapture`, `VideoWriter`, `CAP_PROP_FRAME_WIDTH`, `CAP_PROP_FRAME_HEIGHT` |
| **Imgcodecs**   | 图像文件的读取和保存，支持多种图像格式。                     | `imread`, `imwrite`, `imdecode`, `imencode`                  |
| **Xfeatures2d** | 额外的特征检测与描述算法，如 SIFT、SURF、FREAK 等。          | `SIFT`, `SURF`, `FREAK`, `DAISY`                             |
| **Superres**    | 超分辨率图像处理。                                           | `SuperResolution`, `DenseOpticalFlowExt`                     |
| **Optflow**     | 光流计算和运动分析。                                         | `calcOpticalFlowFarneback`, `calcOpticalFlowPyrLK`           |
| **Cuda**        | 利用 GPU 加速的计算机视觉算法。                              | `cuda::GpuMat`, `cuda::Stream`, `cuda::resize`               |
| **Contrib**     | 社区贡献的额外功能，如人脸识别、文本检测等。                 | `FaceRecognizer`, `TextDetector`                             |

------

### 5.4.1 Core模块

`core` 模块是 OpenCV 的核心模块，提供了基本的数据结构和函数。

**主要功能**

- **基本数据结构**：
  - `Mat`：用于存储图像和矩阵数据。
  - `Point`、`Size`、`Rect`：用于表示点、尺寸和矩形区域。
  - `Scalar`：用于表示颜色或像素值。
- **矩阵操作**：
  - 矩阵的创建、复制、转换、算术运算等。
- **文件 I/O**：
  - 读取和保存图像、视频、XML/YAML 文件等。
- **内存管理**：
  - 自动内存管理，支持引用计数。

```c++
#include <opencv2/core.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 创建一个 3x3 的矩阵
   Mat mat = (Mat_<int>(3, 3) << 1, 2, 3, 4, 5, 6, 7, 8, 9);
 
   // 输出矩阵
   cout << "Matrix:**\n**" << mat << endl;
 
   // 访问矩阵元素
   int value = mat.at<int>(1, 1);
   cout << "Value at (1, 1): " << value << endl;
 
   return 0;
 }
```

### 5.4.2 Imgproc 模块

`imgproc` 模块提供了图像处理功能，包括滤波、几何变换、颜色空间转换等。

**主要功能**

- **图像滤波**：
  - 均值滤波、高斯滤波、中值滤波等。
- **几何变换**：
  - 缩放、旋转、仿射变换、透视变换等。
- **颜色空间转换**：
  - RGB 到灰度、HSV、Lab 等颜色空间的转换。
- **边缘检测**：
  - Canny、Sobel、Laplacian 等边缘检测算法。
- **形态学操作**：
  - 腐蚀、膨胀、开运算、闭运算等。
- **阈值化**：
  - 简单阈值化、自适应阈值化等。

```c++
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
 
 using namespace cv;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
   if (image.empty()) return -1;
 
   // 转换为灰度图像
   Mat grayImage;
   cvtColor(image, grayImage, COLOR_BGR2GRAY);
 
   // 高斯滤波
   Mat blurredImage;
   GaussianBlur(grayImage, blurredImage, Size(5, 5), 0);
 
   // 显示结果
   imshow("Original Image", image);
   imshow("Blurred Image", blurredImage);
   waitKey(0);
 
   return 0;
 }
```

------

### 5.4.3 Highgui 模块

`highgui` 模块提供了图像和视频的显示、窗口管理以及用户交互功能。

**主要功能**

- **图像显示**：
  - 创建窗口、显示图像、等待用户输入。
- **视频捕获**：
  - 从摄像头或视频文件中读取帧。
- **用户交互**：
  - 鼠标事件、滑动条、按钮等。

```c++
#include <opencv2/highgui.hpp>
 
 using namespace cv;
 
 int main() {
   // 读取图像
   Mat image = imread("test.jpg");
   if (image.empty()) return -1;
 
   // 创建窗口并显示图像
   namedWindow("Display Window", WINDOW_AUTOSIZE);
   imshow("Display Window", image);
 
   // 等待用户按键
   waitKey(0);
 
   // 关闭窗口
   destroyAllWindows();
 
   return 0;
 }
```

------

### 5.4.4 Video 模块

`video` 模块提供了视频处理功能，包括视频捕获、背景减除、光流计算等。

> #查看所有的摄像头设备
> v4l2-ctl --list-devices
> #查看摄像头支持的格式
> v4l2-ctl --list-formats-ext -d /dev/video0
> #开启摄像头预览
> gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! autovideosink
>
> #拍照
> gst-launch-1.0 v4l2src device=/dev/video0 num-buffers=1 !video/x-raw,format=NV12,width=640,height=480 ! mppjpegenc !filesink location=pic.jpg
> #录视频 H264格式
> gst-launch-1.0 filesrc location=5695_h264.mp4 !qtdemux !queue !h264parse !mppvideodec !waylandsink

**主要功能**

- **视频捕获**：
  - 从摄像头或视频文件中读取帧。
- **背景减除**：
  - 提取视频中的前景对象。
- **光流计算**：
  - 计算图像中物体的运动。

```c++
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
 
 using namespace cv;
 
 int main() {
   // 打开摄像头
   VideoCapture cap(0);
   if (!cap.isOpened()) return -1;
 
   Mat frame;
   while (true) {
     // 读取一帧
     cap >> frame;
     if (frame.empty()) break;
 
     // 显示帧
     imshow("Camera Feed", frame);
 
     // 按下 ESC 键退出
     if (waitKey(30) == 27) break;
   }
 
   // 释放摄像头并关闭窗口
   cap.release();
   destroyAllWindows();
 
   return 0;
 }
```

### 5.4.5 Calib3d 模块

`calib3d` 模块提供了相机标定、3D 重建、姿态估计等功能。

**主要功能**

- **相机标定**：
  - 计算相机内参和畸变系数。
- **3D 重建**：
  - 从多视图图像中重建 3D 场景。
- **姿态估计**：
  - 估计物体的 3D 姿态。

```c++
#include <opencv2/calib3d.hpp>
#include <opencv2/highgui.hpp>
 
 using namespace cv;
 
 int main() {
   // 读取图像
   Mat image1 = imread("left.jpg");
   Mat image2 = imread("right.jpg");
   if (image1.empty() || image2.empty()) return -1;
 
   // 特征点检测与匹配
   Ptr<Feature2D> detector = ORB::create();
   vector<KeyPoint> keypoints1, keypoints2;
   Mat descriptors1, descriptors2;
   detector->detectAndCompute(image1, noArray(), keypoints1, descriptors1);
   detector->detectAndCompute(image2, noArray(), keypoints2, descriptors2);
 
   BFMatcher matcher(NORM_HAMMING);
   vector<DMatch> matches;
   matcher.match(descriptors1, descriptors2, matches);
 
   // 计算基础矩阵
   vector<Point2f> points1, points2;
   for (const auto& match : matches) {
     points1.push_back(keypoints1[match.queryIdx].pt);
     points2.push_back(keypoints2[match.trainIdx].pt);
   }
   Mat fundamentalMatrix = findFundamentalMat(points1, points2, FM_RANSAC);
 
   // 输出基础矩阵
   cout << "Fundamental Matrix:**\n**" << fundamentalMatrix << endl;
 
   return 0;
 }
```

------

### 5.4.6 DNN 模块

`dnn` 模块提供了深度学习模型的加载和推理功能。

**主要功能**

- **模型加载**：
  - 支持 TensorFlow、PyTorch、Caffe 等框架的模型。
- **推理**：
  - 对图像进行分类、目标检测、语义分割等。

```c++
#include <opencv2/dnn.hpp>
#include <opencv2/highgui.hpp>
 
 using namespace cv;
 using namespace dnn;
 
 int main() {
   // 加载模型
   Net net = readNetFromTensorflow("model.pb", "config.pbtxt");
 
   // 读取图像
   Mat image = imread("test.jpg");
   if (image.empty()) return -1;
 
   // 预处理
   Mat blob = blobFromImage(image, 1.0, Size(300, 300), Scalar(127.5, 127.5, 127.5), true, false);
   net.setInput(blob);
 
   // 推理
   Mat output = net.forward();
 
   // 处理输出
   // ...
 
   return 0;
 }
```

## 5.5 特征检测与描述

特征检测与描述是计算机视觉中的核心技术，用于从图像中提取关键点（Keypoints）并计算其描述符（Descriptors）。这些关键点和描述符可以用于图像匹配、目标识别、3D 重建等任务。

**主要步骤**

- **特征检测**：检测图像中的关键点（如角点、边缘等）。
- **特征描述**：为每个关键点计算描述符，用于表示关键点周围的局部特征。
- **特征匹配**：通过比较描述符，找到不同图像中相似的关键点。
- **特征检测与描述**：通过特征匹配找到两幅图像中相似的关键点，用于图像拼接、全景图生成等。  
- **目标识别**：提取目标图像的特征，与数据库中的特征进行匹配，实现目标识别。 
- **3D** **重建**：通过多视图图像中的特征点匹配，计算相机的位姿并重建 3D 场景。 
- **实时跟踪**：在视频序列中检测和跟踪特征点，用于 SLAM（同步定位与地图构建）等应用。

**常用特征检测与描述算法**

OpenCV 提供了多种特征检测与描述算法，以下是常见的几种：

| **算法**  | **特点**                                                     | **适用场景**       |
| --------- | ------------------------------------------------------------ | ------------------ |
| **SIFT**  | 尺度不变特征变换，对旋转、缩放、亮度变化具有鲁棒性。         | 图像匹配、目标识别 |
| **SURF**  | 加速版的 SIFT，计算速度更快，但对旋转和缩放变化的鲁棒性稍差。 | 实时图像匹配       |
| **ORB**   | 基于 FAST 关键点检测和 BRIEF 描述符，速度快，适合实时应用。  | 实时图像匹配、SLAM |
| **FAST**  | 快速角点检测算法，仅检测关键点，不生成描述符。               | 实时角点检测       |
| **BRIEF** | 二进制描述符，计算速度快，但对旋转和缩放变化的鲁棒性较差。   | 实时图像匹配       |
| **AKAZE** | 基于非线性尺度空间的特征检测与描述算法，对旋转和缩放变化具有鲁棒性。 | 图像匹配、目标识别 |

------

### 5.5.1 角点检测

角点是图像中亮度变化剧烈的点，通常位于物体的边缘或纹理丰富的区域。角点检测是特征检测的基础，常用的角点检测算法有 Harris 角点检测和 Shi-Tomasi 角点检测。

**Harris**角点检测

Harris  角点检测是一种经典的角点检测算法，它通过计算图像中每个像素点的自相关矩阵来判断该点是否为角点。自相关矩阵的特征值可以反映该点的局部结构：如果两个特征值都很大，则该点很可能是角点；如果一个特征值很大，另一个很小，则该点可能是边缘；如果两个特征值都很小，则该点可能是平坦区域。

在 OpenCV 中，可以使用 `cv::cornerHarris` 函数来实现 Harris 角点检测：

```c++
#include <opencv2/opencv.hpp>
 
 int main() {
   cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
   cv::Mat dst, dst_norm;
 
   // Harris角点检测
   cv::cornerHarris(src, dst, 2, 3, 0.04);
 
   // 归一化并显示结果
   cv::normalize(dst, dst_norm, 0, 255, cv::NORM_MINMAX, CV_32FC1, cv::Mat());
   cv::imshow("Harris Corners", dst_norm);
   cv::waitKey(0);
 
   return 0;
 }
```

**Shi-Tomasi 角点检测**

Shi-Tomasi角点检测是对Harris角点检测的改进，它通过计算图像中每个像素点的最小特征值来判断该点是否为角点。与Harris角点检测相比，Shi-Tomasi角点检测更加稳定，且计算量较小。

在OpenCV中，可以使用`cv::goodFeaturesToTrack`函数来实现Shi-Tomasi角点检测：

```c++
#include <opencv2/opencv.hpp>
 
 int main() {
   cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::Point2f> corners;
 
   // Shi-Tomasi角点检测
   cv::goodFeaturesToTrack(src, corners, 100, 0.01, 10);
 
   // 绘制角点
   for (size_t i = 0; i < corners.size(); i++) {
     cv::circle(src, corners[i], 5, cv::Scalar(0, 0, 255), 2);
   }
 
   cv::imshow("Shi-Tomasi Corners", src);
   cv::waitKey(0);
 
   return 0;
 }
```

------

### 5.5.2 特征点检测

特征点检测是提取图像中具有独特性质的点，这些点通常具有旋转、缩放、光照不变性。常用的特征点检测算法有SIFT、SURF和ORB。

**SIFT** **算法**

SIFT（Scale-Invariant Feature Transform）是一种基于尺度空间的特征点检测算法，它对图像的旋转、缩放、亮度变化具有不变性。SIFT算法通过检测图像中的极值点，并计算这些点的梯度方向直方图来生成特征描述子。

OpenCV 4.4 及之后可使用主库中的 `cv::SIFT`；较早版本的示例可能使用 contrib 中的 `cv::xfeatures2d::SIFT`。下面采用前一种接口。

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/features2d.hpp>
 
 int main() {
   cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints;
   cv::Mat descriptors;
 
   // SIFT特征点检测
   cv::Ptr<cv::SIFT> sift = cv::SIFT::create();
   sift->detectAndCompute(src, cv::noArray(), keypoints, descriptors);
 
   // 绘制特征点
   cv::Mat output;
   cv::drawKeypoints(src, keypoints, output);
   cv::imshow("SIFT Keypoints", output);
   cv::waitKey(0);
 
   return 0;
 }
```

**SURF 算法**

SURF（Speeded-Up Robust Features）是对SIFT算法的改进，它通过使用积分图像和Hessian矩阵来加速特征点检测过程。SURF算法在保持较高检测精度的同时，显著提高了计算速度。

SURF 使用 `cv::xfeatures2d::SURF`，需要安装与 OpenCV 版本匹配的 opencv_contrib，并在构建时启用 `OPENCV_ENABLE_NONFREE`；只装主库不能运行这个示例。

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
 
 int main() {
   cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints;
   cv::Mat descriptors;
 
   // SURF特征点检测
   cv::Ptr<cv::xfeatures2d::SURF> surf = cv::xfeatures2d::SURF::create();
   surf->detectAndCompute(src, cv::noArray(), keypoints, descriptors);
 
   // 绘制特征点
   cv::Mat output;
   cv::drawKeypoints(src, keypoints, output);
   cv::imshow("SURF Keypoints", output);
   cv::waitKey(0);
 
   return 0;
 }
```

**ORB 算法**

ORB（Oriented FAST and Rotated BRIEF）是一种结合了FAST角点检测和BRIEF描述子的特征点检测算法。ORB算法具有较高的计算效率，适合实时应用。

在OpenCV中，可以使用`cv::ORB`类来实现ORB特征点检测：

```c++
#include <opencv2/opencv.hpp>
 
 int main() {
   cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints;
   cv::Mat descriptors;
 
   // ORB特征点检测
   cv::Ptr<cv::ORB> orb = cv::ORB::create();
   orb->detectAndCompute(src, cv::noArray(), keypoints, descriptors);
 
   // 绘制特征点
   cv::Mat output;
   cv::drawKeypoints(src, keypoints, output);
   cv::imshow("ORB Keypoints", output);
   cv::waitKey(0);
 
   return 0;
 }
```

------

### 5.5.3 特征匹配

特征匹配是将两幅图像中的特征点进行匹配的过程。常用的特征匹配算法有BFMatcher（暴力匹配器）和FLANN匹配器。

**BFMatcher**

BFMatcher（Brute-Force Matcher）是一种简单的特征匹配算法，它通过计算特征描述子之间的欧氏距离来寻找最佳匹配点。BFMatcher适用于特征点数量较少的情况。

在OpenCV中，可以使用`cv::BFMatcher`类来实现BFMatcher：

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
 
 int main() {
   cv::Mat src1 = cv::imread("image1.jpg", cv::IMREAD_GRAYSCALE);
   cv::Mat src2 = cv::imread("image2.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints1, keypoints2;
   cv::Mat descriptors1, descriptors2;
 
   // SIFT特征点检测
   cv::Ptr<cv::xfeatures2d::SIFT> sift = cv::xfeatures2d::SIFT::create();
   sift->detectAndCompute(src1, cv::noArray(), keypoints1, descriptors1);
   sift->detectAndCompute(src2, cv::noArray(), keypoints2, descriptors2);
 
   // BFMatcher匹配
   cv::BFMatcher matcher(cv::NORM_L2);
   std::vector<cv::DMatch> matches;
   matcher.match(descriptors1, descriptors2, matches);
 
   // 绘制匹配结果
   cv::Mat output;
   cv::drawMatches(src1, keypoints1, src2, keypoints2, matches, output);
   cv::imshow("BFMatcher Matches", output);
   cv::waitKey(0);
 
   return 0;
 }
```

 **FLANN 匹配器**

FLANN（Fast Library for Approximate Nearest Neighbors）是一种近似最近邻搜索算法，它通过构建KD树或K-means树来加速特征匹配过程。FLANN匹配器适用于特征点数量较多的情况。

在OpenCV中，可以使用`cv::FlannBasedMatcher`类来实现FLANN匹配器：

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
 
 int main() {
   cv::Mat src1 = cv::imread("image1.jpg", cv::IMREAD_GRAYSCALE);
   cv::Mat src2 = cv::imread("image2.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints1, keypoints2;
   cv::Mat descriptors1, descriptors2;
 
   // SIFT特征点检测
   cv::Ptr<cv::xfeatures2d::SIFT> sift = cv::xfeatures2d::SIFT::create();
   sift->detectAndCompute(src1, cv::noArray(), keypoints1, descriptors1);
   sift->detectAndCompute(src2, cv::noArray(), keypoints2, descriptors2);
 
   // FLANN匹配器
   cv::FlannBasedMatcher matcher;
   std::vector<cv::DMatch> matches;
   matcher.match(descriptors1, descriptors2, matches);
 
   // 绘制匹配结果
   cv::Mat output;
   cv::drawMatches(src1, keypoints1, src2, keypoints2, matches, output);
   cv::imshow("FLANN Matches", output);
   cv::waitKey(0);
 
   return 0;
 }
```

### 5.5.4 特征点匹配与筛选

在实际应用中，特征点匹配结果中可能存在一些错误的匹配对。为了提高匹配的准确性，通常需要对匹配结果进行筛选。常用的筛选方法有基于距离的筛选和基于几何约束的筛选。

**基于距离的筛选**

基于距离的筛选是通过设置一个阈值来过滤掉距离较大的匹配对。OpenCV中可以使用`cv::DescriptorMatcher::radiusMatch`函数来实现基于距离的筛选。

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
 
 int main() {
   cv::Mat src1 = cv::imread("image1.jpg", cv::IMREAD_GRAYSCALE);
   cv::Mat src2 = cv::imread("image2.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints1, keypoints2;
   cv::Mat descriptors1, descriptors2;
 
   // SIFT特征点检测
   cv::Ptr<cv::xfeatures2d::SIFT> sift = cv::xfeatures2d::SIFT::create();
   sift->detectAndCompute(src1, cv::noArray(), keypoints1, descriptors1);
   sift->detectAndCompute(src2, cv::noArray(), keypoints2, descriptors2);
 
   // BFMatcher匹配
   cv::BFMatcher matcher(cv::NORM_L2);
   std::vector<std::vector<cv::DMatch>> matches;
   matcher.radiusMatch(descriptors1, descriptors2, matches, 50.0);
 
   // 绘制匹配结果
   cv::Mat output;
   cv::drawMatches(src1, keypoints1, src2, keypoints2, matches, output);
   cv::imshow("Filtered Matches", output);
   cv::waitKey(0);
 
   return 0;
 }
```

**基于几何约束的筛选**

基于几何约束的筛选是通过计算基础矩阵或单应性矩阵来过滤掉不符合几何约束的匹配对。OpenCV中可以使用`cv::findFundamentalMat`或`cv::findHomography`函数来实现基于几何约束的筛选。

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
 
 int main() {
   cv::Mat src1 = cv::imread("image1.jpg", cv::IMREAD_GRAYSCALE);
   cv::Mat src2 = cv::imread("image2.jpg", cv::IMREAD_GRAYSCALE);
   std::vector<cv::KeyPoint> keypoints1, keypoints2;
   cv::Mat descriptors1, descriptors2;
 
   // SIFT特征点检测
   cv::Ptr<cv::xfeatures2d::SIFT> sift = cv::xfeatures2d::SIFT::create();
   sift->detectAndCompute(src1, cv::noArray(), keypoints1, descriptors1);
   sift->detectAndCompute(src2, cv::noArray(), keypoints2, descriptors2);
 
   // BFMatcher匹配
   cv::BFMatcher matcher(cv::NORM_L2);
   std::vector<cv::DMatch> matches;
   matcher.match(descriptors1, descriptors2, matches);
 
   // 基于几何约束的筛选
   std::vector<cv::Point2f> points1, points2;
   for (size_t i = 0; i < matches.size(); i++) {
     points1.push_back(keypoints1[matches[i].queryIdx].pt);
     points2.push_back(keypoints2[matches[i].trainIdx].pt);
   }
 
   cv::Mat mask;
   cv::findHomography(points1, points2, cv::RANSAC, 3, mask);
 
   // 筛选匹配对
   std::vector<cv::DMatch> good_matches;
   for (size_t i = 0; i < matches.size(); i++) {
     if (mask.at<uchar>(i)) {
       good_matches.push_back(matches[i]);
     }
   }
 
   // 绘制匹配结果
   cv::Mat output;
   cv::drawMatches(src1, keypoints1, src2, keypoints2, good_matches, output);
   cv::imshow("Filtered Matches", output);
   cv::waitKey(0);
 
   return 0;
 }
```

## 5.6 高级图像处理

高级图像处理是指在基础图像处理（如滤波、边缘检测等）的基础上，进一步实现更复杂的任务，例如图像分割、轮廓检测、形态学操作、直方图处理等。这些技术广泛应用于目标检测、图像分析、医学影像处理等领域。

**高级图像处理的应用场景**

**医学影像分析：**

- 使用图像分割技术提取病变区域。
- 使用形态学操作去除噪声。

**目标检测与跟踪：**

- 使用轮廓检测和模板匹配定位目标。
- 使用直方图处理增强目标特征。

**图像增强：**

- 使用直方图均衡化提高图像对比度。
- 使用分水岭算法分离重叠对象。

------

### 5.6.1 图像分割

图像分割是图像处理中的一个重要步骤，它将图像划分为多个区域或对象，以便于进一步的分析和处理。常见的图像分割方法包括基于阈值的分割、基于边缘的分割和基于区域的分割。

**基于阈值的分割**

基于阈值的分割是最简单的图像分割方法之一。它通过设定一个或多个阈值，将图像的像素值分为不同的类别。常见的阈值分割方法包括全局阈值和自适应阈值。

**全局阈值分割**

全局阈值分割使用一个固定的阈值将图像分为前景和背景。OpenCV 提供了 `cv::threshold` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
cv::Mat dst;
cv::threshold(src, dst, 128, 255, cv::THRESH_BINARY);
```

以上代码中，`128` 是阈值，`255` 是最大像素值，`cv::THRESH_BINARY` 表示使用二值化方法。

**自适应阈值分割**

自适应阈值分割根据图像的局部区域动态调整阈值。OpenCV 提供了 `cv::adaptiveThreshold` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
cv::Mat dst;
cv::adaptiveThreshold(src, dst, 255, cv::ADAPTIVE_THRESH_MEAN_C, cv::THRESH_BINARY, 11, 2);
```

以上代码中，`255` 是最大像素值，`cv::ADAPTIVE_THRESH_MEAN_C` 表示使用局部均值作为阈值，`11` 是邻域大小，`2` 是常数。

**基于边缘的分割**

基于边缘的分割通过检测图像中的边缘来分割图像。常见的边缘检测算法包括 Canny 边缘检测和 Sobel 算子。

**Canny** **边缘检测**

Canny 边缘检测是一种多阶段的边缘检测算法。OpenCV 提供了 `cv::Canny` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
cv::Mat edges;
cv::Canny(src, edges, 100, 200);
```

以上代码中，`100` 和 `200` 是 Canny 算法的两个阈值。

**基于区域的分割**（分水岭算法）

基于区域的分割通过将图像划分为多个区域来实现分割。分水岭算法是一种常用的基于区域的分割方法。

**分水岭算法**

分水岭算法将图像视为地形图，通过模拟水流的扩散来分割图像。OpenCV 提供了 `cv::watershed` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg");
cv::Mat markers = cv::Mat::zeros(src.size(), CV_32S);
cv::watershed(src, markers);
```

以上代码中，`markers` 是标记矩阵，用于存储分割结果。

------

### 5.6.2 轮廓检测

轮廓检测是图像处理中的一个重要步骤，它用于检测图像中的对象边界。OpenCV 提供了多种轮廓检测和处理的函数。

**查找轮廓**

查找轮廓是轮廓检测的第一步。OpenCV 提供了 `cv::findContours` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg", cv::IMREAD_GRAYSCALE);
std::vector<std::vector<cv::Point>> contours;
std::vector<cv::Vec4i> hierarchy;
cv::findContours(src, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);
```

> ### 1. image - 输入图像
>
> - **类型**：8位单通道二值图像
> - **要求**：必须是二值图像（黑白图像），非零像素被视为1，零像素被视为0
> - **预处理**：通常需要先进行阈值处理或边缘检测
>
> ### 2. contours - 输出轮廓
>
> - **类型**：`vector<vector<Point>>`
> - **说明**：存储检测到的轮廓，每个轮廓是一系列点的集合
> - **示例**：`contours[i]` 表示第i个轮廓，包含该轮廓的所有点
>
> ### 3. hierarchy - 层次信息（可选）
>
> - **类型**：`vector<Vec4i>`
> - **说明**：描述轮廓之间的层次关系，每个元素包含4个整数：
>   - `hierarchy[i][0]`：下一个同级轮廓的索引
>   - `hierarchy[i][1]`：前一个同级轮廓的索引
>   - `hierarchy[i][2]`：第一个子轮廓的索引
>   - `hierarchy[i][3]`：父轮廓的索引
> - **如果不需要层次信息**：可以传入`noArray()`
>
> ### 4. mode - 轮廓检索模式
>
> | 模式       | 常量            | 说明                             |
> | ---------- | --------------- | -------------------------------- |
> | 仅外部轮廓 | `RETR_EXTERNAL` | 只检测最外层轮廓                 |
> | 所有轮廓   | `RETR_LIST`     | 检测所有轮廓，无层次关系         |
> | 树状结构   | `RETR_TREE`     | 检测所有轮廓，建立完整的层次结构 |
> | 两级层次   | `RETR_CCOMP`    | 检测所有轮廓，组织为两级层次     |
>
> ### 5. method - 轮廓近似方法
>
> | 方法         | 常量                     | 说明                           |
> | ------------ | ------------------------ | ------------------------------ |
> | 存储所有点   | `CHAIN_APPROX_NONE`      | 存储轮廓上的所有点             |
> | 压缩冗余点   | `CHAIN_APPROX_SIMPLE`    | 压缩水平、垂直、对角线方向的点 |
> | Teh-Chin算法 | `CHAIN_APPROX_TC89_L1`   | 应用Teh-Chin链近似算法         |
> | Teh-Chin算法 | `CHAIN_APPROX_TC89_KCOS` | 应用Teh-Chin链近似算法         |

以上代码中，`contours` 是存储轮廓的向量，`hierarchy` 是存储轮廓层次结构的向量。

**轮廓特征**

轮廓特征包括面积、周长、边界框等。OpenCV 提供了多种函数来计算这些特征。

**面积**

面积是轮廓的一个重要特征。OpenCV 提供了 `cv::contourArea` 函数来计算轮廓的面积。

```
double area = cv::contourArea(contours[0]);
```

**周长**

周长是轮廓的另一个重要特征。OpenCV 提供了 `cv::arcLength` 函数来计算轮廓的周长。

```
double perimeter = cv::arcLength(contours[0], true);
```

**边界框**

边界框是轮廓的最小外接矩形。OpenCV 提供了 `cv::boundingRect` 函数来计算边界框。

```
cv::Rect rect = cv::boundingRect(contours[0]);
```

**轮廓绘制**

轮廓绘制是将检测到的轮廓绘制到图像上。OpenCV 提供了 `cv::drawContours` 函数来实现这一功能。

```
cv::Mat dst = cv::Mat::zeros(src.size(), CV_8UC3);
cv::drawContours(dst, contours, -1, cv::Scalar(0, 255, 0), 2);
```

以上代码中，`dst` 是绘制轮廓后的图像，`cv::Scalar(0, 255, 0)` 是轮廓的颜色，`2` 是轮廓的线宽。

------

### 5.6.3 模板匹配

模板匹配是一种在图像中查找特定模板的方法。OpenCV 提供了 `cv::matchTemplate` 函数来实现这一功能。

**单模板匹配**

单模板匹配是在图像中查找一个模板。OpenCV 提供了 `cv::matchTemplate` 函数来实现这一功能。

```
cv::Mat src = cv::imread("image.jpg");
cv::Mat templ = cv::imread("template.jpg");
cv::Mat result;
cv::matchTemplate(src, templ, result, cv::TM_CCOEFF_NORMED);
```

以上代码中，`result` 是匹配结果矩阵，`cv::TM_CCOEFF_NORMED` 是匹配方法。

**多模板匹配**

多模板匹配是在图像中查找多个模板。可以通过遍历匹配结果矩阵来实现多模板匹配。

```
double minVal, maxVal;
cv::Point minLoc, maxLoc;
cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);
```

以上代码中，`maxLoc` 是匹配结果的最大值位置。

------

### 5.6.4 实验

#### 5.6.4.1 分水岭算法

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("objects.jpg");
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 转换为灰度图像
   Mat gray;
   cvtColor(image, gray, COLOR_BGR2GRAY);
 
   // 二值化
   Mat binary;
   threshold(gray, binary, 0, 255, THRESH_BINARY_INV + THRESH_OTSU);
 
   // 去除噪声
   Mat kernel = getStructuringElement(MORPH_RECT, Size(3, 3));
   morphologyEx(binary, binary, MORPH_OPEN, kernel, Point(-1, -1), 2);
 
   // 计算距离变换
   Mat dist;
   distanceTransform(binary, dist, DIST_L2, 5);
 
   // 归一化距离变换图像
   normalize(dist, dist, 0, 1.0, NORM_MINMAX);
 
   // 二值化距离变换图像
   threshold(dist, dist, 0.5, 1.0, THRESH_BINARY);
 
   // 查找轮廓
   Mat dist_8u;
   dist.convertTo(dist_8u, CV_8U);
   vector<vector<Point>> contours;
   findContours(dist_8u, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
 
   // 创建标记图像
   Mat markers = Mat::zeros(dist.size(), CV_32S);
   for (size_t i = 0; i < contours.size(); i++) {
     drawContours(markers, contours, static_cast<int>(i), Scalar(static_cast<int>(i) + 1), -1);
   }
 
   // 应用分水岭算法
   watershed(image, markers);
 
   // 显示结果
   Mat result = image.clone();
   for (int i = 0; i < markers.rows; i++) {
     for (int j = 0; j < markers.cols; j++) {
       if (markers.at<int>(i, j) == -1) {
         result.at<Vec3b>(i, j) = Vec3b(0, 255, 0); // 标记边界为绿色
       }
     }
   }
 
   imshow("Watershed Result", result);
   waitKey(0);
 
   return 0;
 }
```

#### 5.6.4.2 轮廓检测

轮廓检测用于提取图像中对象的边界。

OpenCV 提供了 findContours 函数来检测轮廓。

```c++
#include <iostream>
#include <opencv2/opencv.hpp>

int main(){
    // 打开摄像头
    cv::VideoCapture cap(0);
    if(!cap.isOpened()){
        std::cout << "打开摄像头失败" << std::endl;
        return -1;
    }
    
    while(1){
        //读取摄像头数据
        cv::Mat img;
        cap >> img;
        if(img.empty()){
            std::cout << "读取摄像头数据失败" << std::endl;
            return -1;
        }

        // 读取图片
        //cv::Mat img = cv::imread("./woniu.png");
        if(img.empty()){
            std::cout << "读取图片失败" << std::endl;
            return -1;
        }
        int height = img.rows;
        int width = img.cols;
        int channel_count = img.channels();
        //std::cout << "图片的通道数为：" << channel_count << std::endl;
        float scale = 0.5;
        // 缩放图片
        //cv::Mat resizedImage;
        //cv::resize(img, img, cv::Size(width*scale, height*scale));

        //cv::Mat img_gray;
        // 颜色转换
        //cv::cvtColor(img, img_gray, cv::COLOR_BGR2GRAY);  // 转换为灰度图
        //int threshold_value = 50;
        //cv::Mat bin;
        //二值化  threshold阈值
        //cv::threshold(img_gray, bin, threshold_value, 255, cv::THRESH_BINARY);

        // 分离通道
        std::vector<cv::Mat> channels;
        cv::split(img, channels);
        // 红色通道
        cv::Mat red_channel = channels[2];
        // 绿色通道
        cv::Mat green_channel = channels[1];
        // 蓝色通通
        cv::Mat blue_channel = channels[0];
        //计算一个红色的阈值
        /**
         * red_channel > 160 过滤掉灰色部分
         * red_channel > blue_channel*1.3 过滤掉偏紫部分
         * red_channel > green_channel*1.3 过滤掉偏黄部分
         */
        cv::Mat red_threshold = (red_channel > 160)&(red_channel > blue_channel*1.3)&(red_channel > green_channel*1.3);
        cv::Mat red;
        // 转为0-255的数据
        red_threshold.convertTo(red, CV_8UC1, 255);

        // 降噪
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(10, 10));  // 定义结构元素
        cv::morphologyEx(red, red, cv::MORPH_OPEN, kernel);  // 开运算降噪
        cv::morphologyEx(red, red, cv::MORPH_CLOSE, kernel);  // 闭运算降噪

        // 查找轮廓
        std::vector<std::vector<cv::Point>> contours;  //存储轮廓的变量
        /**
         * 参数1： 输入图像
         * 参数2： 轮廓的集合
         * 参数3： 轮廓检索模式，这里是RETR_EXTERNAL，表示只检测外轮廓
         * 参数4： 轮廓近似办法，这里是CHAIN_APPROX_SIMPLE，表示压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标。
         */
        cv::findContours(red, contours, cv::RETR_LIST, cv::CHAIN_APPROX_SIMPLE);
        
        
        //输出轮廓的面积
        for(int i = 0; i < contours.size(); i++){
            //用于存储文字的变量
            char text[128];
            memset(text, 0, sizeof(text));
            cv::Rect rect = cv::boundingRect(contours[i]);
            sprintf(text, "idx:%d area:%.0f pos:%d %d %d %d", i+1, cv::contourArea(contours[i]), rect.x, rect.y, rect.width, rect.height);
            //std::cout << text;
            cv::putText(img, text, cv::Point(0, 30*(i+1)), cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 255), 1);  // 绘制文字
        }
        // 绘制轮廓
        cv::drawContours(img, contours, -1, cv::Scalar(0, 255, 0), 1);  // 绘制轮廓，-1表示绘制所有轮廓

        // 保存图片
        //cv::imwrite("output.jpg", resizedImage);
        // 显示图片
        cv::imshow("img", img);
        // 等待按键按下
        // 延时33ms
        cv::waitKey(33);
    }
    return 0;
}
```

#### 5.6.4.3 形态学操作

形态学操作是基于形状的图像处理技术，常用于去除噪声、分离对象等。

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("noisy_image.jpg");
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 转换为灰度图像
   Mat gray;
   cvtColor(image, gray, COLOR_BGR2GRAY);
 
   // 二值化
   Mat binary;
   threshold(gray, binary, 0, 255, THRESH_BINARY_INV + THRESH_OTSU);
 
   // 定义核
   Mat kernel = getStructuringElement(MORPH_RECT, Size(5, 5));
 
   // 开运算（去除噪声）
   Mat opened;
   morphologyEx(binary, opened, MORPH_OPEN, kernel);
 
   // 闭运算（填充孔洞）
   Mat closed;
   morphologyEx(opened, closed, MORPH_CLOSE, kernel);
 
   // 显示结果
   imshow("Original Binary", binary);
   imshow("Opened Image", opened);
   imshow("Closed Image", closed);
   waitKey(0);
 
   return 0;
 }
```

#### 5.6.4.4 直方图处理

直方图处理用于分析图像的像素分布，常见的操作包括直方图均衡化、直方图匹配等。

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像
   Mat image = imread("low_contrast.jpg");
   if (image.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 转换为灰度图像
   Mat gray;
   cvtColor(image, gray, COLOR_BGR2GRAY);
 
   // 直方图均衡化
   Mat equalized;
   equalizeHist(gray, equalized);
 
   // 显示结果
   imshow("Original Image", gray);
   imshow("Equalized Image", equalized);
   waitKey(0);
 
   return 0;
 }
```

#### 5.6.4.5 模板匹配

模板匹配用于在图像中查找与模板相似的区域。

```c++
 #include <opencv2/opencv.hpp>
 #include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 读取图像和模板
   Mat image = imread("scene.jpg");
   Mat templ = imread("template.jpg");
   if (image.empty() || templ.empty()) {
     cout << "错误：无法加载图像，请检查路径是否正确。" << endl;
     return -1;
   }
 
   // 模板匹配
   Mat result;
   matchTemplate(image, templ, result, TM_CCOEFF_NORMED);
 
   // 找到最佳匹配位置
   double minVal, maxVal;
   Point minLoc, maxLoc;
   minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);
 
   // 绘制矩形框
   rectangle(image, maxLoc, Point(maxLoc.x + templ.cols, maxLoc.y + templ.rows), Scalar(0, 255, 0), 2);
 
   // 显示结果
   imshow("Template Matching", image);
   waitKey(0);
 
   return 0;
 }
```

## 5.7 视频处理

视频处理是指对视频序列中的每一帧图像进行处理和分析。

OpenCV 提供了强大的工具来处理视频数据，包括视频的读取、帧处理、视频保存以及实时视频处理等功能。

**视频处理的应用场景**

**视频监控:**

- 使用背景减除检测运动物体。
- 使用光流分析物体运动轨迹。

**视频分析:**

- 提取视频中的关键帧。
- 分析视频中的对象行为。

**实时处理:**

- 实时视频滤镜（如边缘检测、模糊等）。
- 实时目标检测与跟踪。

------

### 5.7.1 视频的读取与显示

**读取视频文件**（VideoCapture）

在 OpenCV 中，`VideoCapture` 类用于从视频文件或摄像头中读取视频帧。

要读取一个视频文件，首先需要创建一个 `VideoCapture` 对象，并指定视频文件的路径。

```c++
#include <opencv2/opencv.hpp>
 using namespace cv;
 
 int main() {
   // 创建 VideoCapture 对象并打开视频文件
   VideoCapture cap("example.mp4");
 
   // 检查视频是否成功打开
   if (!cap.isOpened()) {
     std::cerr << "Error: Could not open video file." << std::endl;
     return -1;
   }
 
   // 视频读取与显示代码将在下面介绍
   return 0;
 }
```

**显示视频帧**

读取视频文件后，可以通过循环逐帧读取视频，并使用 `imshow` 函数显示每一帧。

```c++
Mat frame;
 while (true) {
   // 读取下一帧
   cap >> frame;
 
   // 如果帧为空，说明视频已经结束
   if (frame.empty()) {
     break;
   }
 
   // 显示当前帧
   imshow("Video", frame);
 
   // 等待30毫秒，按下ESC键退出
   if (waitKey(30) == 27) {
     break;
   }
 }
 
 // 释放 VideoCapture 对象
 cap.release();
 // 关闭所有窗口
 destroyAllWindows();
```

### 5.7.2 保存视频（VideoWriter）

如果你想要将处理后的视频保存到文件中，可以使用 `VideoWriter` 类。首先需要指定输出文件的名称、编码格式、帧率和帧大小。

```c++
// 获取视频的帧率和帧大小
 double fps = cap.get(CAP_PROP_FPS);
 Size frameSize(cap.get(CAP_PROP_FRAME_WIDTH), cap.get(CAP_PROP_FRAME_HEIGHT));
 
 // 创建 VideoWriter 对象
 VideoWriter writer("output.avi", VideoWriter::fourcc('M', 'J', 'P', 'G'), fps, frameSize);
 
 while (true) {
   cap >> frame;
   if (frame.empty()) {
     break;
   }
 
   // 将帧写入输出视频文件
   writer.write(frame);
 
   imshow("Video", frame);
   if (waitKey(30) == 27) {
     break;
   }
 }
 
 // 释放 VideoCapture 和 VideoWriter 对象
 cap.release();
 writer.release();
 destroyAllWindows();
```

------

### 5.7.3 视频帧处理

**逐帧处理视频**

在视频处理中，通常需要对每一帧进行特定的处理操作。例如，可以对每一帧进行灰度化、边缘检测等操作。

```c++
while (true) {
   cap >> frame;
   if (frame.empty()) {
     break;
   }
 
   // 将帧转换为灰度图像
   Mat grayFrame;
   cvtColor(frame, grayFrame, COLOR_BGR2GRAY);
 
   // 显示灰度帧
   imshow("Gray Video", grayFrame);
 
   if (waitKey(30) == 27) {
     break;
   }
 }
```

**视频帧的实时处理**

实时处理视频帧时，通常需要在每一帧上应用一些实时处理算法。例如，实时检测视频中的运动物体。

```c++
Mat prevFrame, nextFrame, diffFrame;
 cap >> prevFrame;
 cvtColor(prevFrame, prevFrame, COLOR_BGR2GRAY);
 
 while (true) {
   cap >> nextFrame;
   if (nextFrame.empty()) {
     break;
   }
 
   cvtColor(nextFrame, nextFrame, COLOR_BGR2GRAY);
 
   // 计算帧间差异
   absdiff(prevFrame, nextFrame, diffFrame);
 
   // 显示差异帧
   imshow("Motion Detection", diffFrame);
 
   // 更新前一帧
   prevFrame = nextFrame.clone();
 
   if (waitKey(30) == 27) {
     break;
   }
 }
```

------

### 5.7.4 摄像头实时处理

**打开摄像头**

使用 `VideoCapture` 类不仅可以读取视频文件，还可以打开摄像头进行实时视频流的处理。要打开摄像头，只需将 `VideoCapture` 的参数设置为0（表示默认摄像头）。

```c++
VideoCapture cap(0);
 
 if (!cap.isOpened()) {
   std::cerr << "Error: Could not open camera." << std::endl;
   return -1;
 }
```

**实时视频流的处理**

打开摄像头后，可以像处理视频文件一样逐帧处理实时视频流。例如，可以在实时视频流中应用边缘检测算法。

```c++
while (true) {
   cap >> frame;
   if (frame.empty()) {
     break;
   }
 
   // 应用Canny边缘检测
   Mat edges;
   Canny(frame, edges, 100, 200);
 
   // 显示边缘检测结果
   imshow("Edges", edges);
 
   if (waitKey(30) == 27) {
     break;
   }
 }
 
 cap.release();
 destroyAllWindows();
```

------

### 5.7.5 高级视频处理技术

**视频背景减除**

背景减除用于从视频中提取前景对象。

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 打开视频文件或摄像头
   VideoCapture cap("video.mp4");
   if (!cap.isOpened()) {
     cout << "错误：无法打开视频文件或摄像头！" << endl;
     return -1;
   }
 
   // 创建背景减除器
   Ptr<BackgroundSubtractor> bgSubtractor = createBackgroundSubtractorMOG2();
 
   // 处理视频帧
   Mat frame, fgMask;
   while (true) {
     cap >> frame;
     if (frame.empty()) break;
 
     // 应用背景减除
     bgSubtractor->apply(frame, fgMask);
 
     // 显示结果
     imshow("Frame", frame);
     imshow("Foreground Mask", fgMask);
 
     // 按下 ESC 键退出
     if (waitKey(30) == 27) break;
   }
 
   // 释放资源
   cap.release();
   destroyAllWindows();
 
   return 0;
 }
```

**光流计算**

光流用于计算视频帧中物体的运动。

**稀疏光流（Lucas-Kanade 方法）:**

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 打开视频文件或摄像头
   VideoCapture cap("video.mp4");
   if (!cap.isOpened()) {
     cout << "错误：无法打开视频文件或摄像头！" << endl;
     return -1;
   }
 
   // 读取第一帧
   Mat oldFrame, oldGray;
   cap >> oldFrame;
   cvtColor(oldFrame, oldGray, COLOR_BGR2GRAY);
 
   // 选择特征点
   vector<Point2f> oldPoints;
   goodFeaturesToTrack(oldGray, oldPoints, 100, 0.3, 7);
 
   // 处理视频帧
   Mat frame, gray;
   while (true) {
     cap >> frame;
     if (frame.empty()) break;
 
     // 转换为灰度图像
     cvtColor(frame, gray, COLOR_BGR2GRAY);
 
     // 计算光流
     vector<Point2f> newPoints;
     vector<uchar> status;
     vector<float> err;
     calcOpticalFlowPyrLK(oldGray, gray, oldPoints, newPoints, status, err);
 
     // 绘制光流轨迹
     for (size_t i = 0; i < oldPoints.size(); i++) {
       if (status[i]) {
         line(frame, oldPoints[i], newPoints[i], Scalar(0, 255, 0), 2);
         circle(frame, newPoints[i], 3, Scalar(0, 0, 255), -1);
       }
     }
 
     // 更新帧和特征点
     oldGray = gray.clone();
     oldPoints = newPoints;
 
     // 显示结果
     imshow("Optical Flow", frame);
 
     // 按下 ESC 键退出
     if (waitKey(30) == 27) break;
   }
 
   // 释放资源
   cap.release();
   destroyAllWindows();
 
   return 0;
 }
```

## 5.8 机器学习与深度学习

OpenCV 不仅支持传统的计算机视觉任务，还提供了丰富的机器学习和深度学习功能，通过这些功能，可以实现图像分类、目标检测、语义分割等复杂任务。

- **机器学习**：OpenCV 提供了多种传统机器学习算法，如 KNN、SVM、决策树等。
- **深度学习**：OpenCV 的 DNN 模块支持加载和运行预训练的深度学习模型（如 TensorFlow、PyTorch、Caffe 等）。

**机器学习与深度学习的应用场景**

**图像分类:**

- 使用机器学习或深度学习模型对图像进行分类。
- 应用场景：医学影像分类、工业质检等。

**目标检测:**

- 使用深度学习模型检测图像中的目标。
- 应用场景：自动驾驶、安防监控等。

**语义分割:**

- 使用深度学习模型对图像中的每个像素进行分类。
- 应用场景：医学影像分析、遥感图像分析等。

### 5.8.1 机器学习

**常用机器学习算法**

OpenCV 提供了以下常见的机器学习算法：

| **算法**     | **描述**                         |
| ------------ | -------------------------------- |
| **KNN**      | K 近邻算法，用于分类和回归。     |
| **SVM**      | 支持向量机，用于分类和回归。     |
| **决策树**   | 基于树结构的分类和回归算法。     |
| **随机森林** | 基于多个决策树的集成学习算法。   |
| **K-Means**  | 聚类算法，用于将数据分为多个簇。 |

#### 5.8.1.1 K 均值聚类（K-Means）

K 均值聚类是一种无监督学习算法，主要用于将数据集划分为K个簇。每个簇由距离其中心点最近的样本组成。

K-Means 算法的核心思想是通过迭代优化簇中心，使得每个样本点到其所属簇中心的距离最小。

**实现步骤**：

1. **初始化**：随机选择K个样本作为初始簇中心。
2. **分配**：将每个样本分配到距离最近的簇中心。
3. **更新**：重新计算每个簇的中心点。
4. **迭代**：重复步骤2和3，直到簇中心不再变化或达到最大迭代次数。

**OpenCV 中的 K-Means：**

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 int main() {
   // 生成一些随机数据
   cv::Mat data(100, 2, CV_32F);
   cv::randu(data, cv::Scalar(0, 0), cv::Scalar(100, 100));
 
   // 设置K值和迭代条件
   int K = 3;
   cv::Mat labels, centers;
   cv::kmeans(data, K, labels, cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER, 10, 1.0), 3, cv::KMEANS_PP_CENTERS, centers);
 
   // 输出结果
   std::cout << "Labels: " << labels << std::endl;
   std::cout << "Centers: " << centers << std::endl;
 
   return 0;
 }
```

以上代码中，我们生成了100个二维数据点，并使用K-Means算法将其分为3个簇。`cv::kmeans`函数的参数包括数据、簇数、标签、终止条件等。

#### 5.8.1.2 支持向量机（SVM）

支持向量机（SVM）是一种有监督学习算法，主要用于分类和回归任务。

SVM 的核心思想是找到一个超平面，使得不同类别的样本点之间的间隔最大化。

**实现步骤**：

1. **训练**：通过训练数据找到一个最优超平面。
2. **预测**：使用训练好的模型对新数据进行分类。

**OpenCV中的SVM：**

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 int main() {
   // 生成一些训练数据
   cv::Mat trainData = (cv::Mat_<float>(4, 2) << 1, 1, 1, 2, 2, 1, 2, 2);
   cv::Mat labels = (cv::Mat_<int>(4, 1) << 1, 1, -1, -1);
 
   // 创建SVM模型
   cv::Ptr<cv::ml::SVM> svm = cv::ml::SVM::create();
   svm->setKernel(cv::ml::SVM::LINEAR);
   svm->setType(cv::ml::SVM::C_SVC);
   svm->setC(1);
 
   // 训练模型
   svm->train(trainData, cv::ml::ROW_SAMPLE, labels);
 
   // 预测新数据
   cv::Mat testData = (cv::Mat_<float>(1, 2) << 1.5, 1.5);
   float response = svm->predict(testData);
   std::cout << "Predicted label: " << response << std::endl;
 
   return 0;
 }
```

以上代码中，我们使用 SVM 对二维数据进行分类。

`cv::ml::SVM::create()` 用于创建 SVM 模型，`train` 方法用于训练模型，`predict`方法用于预测新数据的类别。

#### 5.8.1.3 主成分分析（PCA）

主成分分析（PCA）是一种降维技术，主要用于减少数据集的维度，同时保留数据的主要特征。

PCA通过线性变换将原始数据映射到一个新的坐标系中，使得数据在新坐标系中的方差最大化。

**实现步骤**：

1. **计算协方差矩阵**：计算数据集的协方差矩阵。
2. **特征值分解**：对协方差矩阵进行特征值分解，得到特征向量和特征值。
3. **选择主成分**：选择前K个最大的特征值对应的特征向量作为主成分。
4. **数据投影**：将原始数据投影到主成分上，得到降维后的数据。

**OpenCV中的PCA：**

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 int main() {
   // 生成一些数据
   cv::Mat data = (cv::Mat_<float>(4, 2) << 1, 2, 2, 3, 3, 4, 4, 5);
 
   // 创建PCA对象
   cv::PCA pca(data, cv::Mat(), cv::PCA::DATA_AS_ROW, 1);
 
   // 投影数据
   cv::Mat projected = pca.project(data);
   std::cout << "Projected data: " << projected << std::endl;
 
   return 0;
 }
```

以上代码中，我们使用PCA对二维数据进行降维。`cv::PCA`类的构造函数接受输入数据、均值向量、数据排列方式和保留的主成分数。`project`方法用于将数据投影到主成分上。

------

### 5.8.2 深度学习

随着深度学习在计算机视觉领域的广泛应用，OpenCV 也提供了对深度学习的支持。

通过 OpenCV 的 DNN 模块，开发者可以加载预训练的深度学习模型，并进行图像分类、目标检测、语义分割等任务。

#### 5.8.2.1 加载预训练的深度学习模型（DNN 模块）

OpenCV 的 DNN 模块支持加载多种深度学习框架（如TensorFlow、Caffe、PyTorch等）的预训练模型。

通过 DNN 模块，开发者可以轻松地将深度学习模型集成到 C++ 应用程序中。

**加载模型**：

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
 
 int main() {
   // 加载预训练的Caffe模型
   cv::dnn::Net net = cv::dnn::readNetFromCaffe("deploy.prototxt", "model.caffemodel");
 
   // 检查模型是否加载成功
   if (net.empty()) {
     std::cerr << "Failed to load model!" << std::endl;
     return -1;
   }
 
   std::cout << "Model loaded successfully!" << std::endl;
 
   return 0;
 }
```

以上代码中，我们使用`cv::dnn::readNetFromCaffe` 函数加载了一个 Caffe 模型。`deploy.prototxt` 是模型的配置文件，`model.caffemodel`是 模型的权重文件。

#### 5.8.2.2 图像分类、目标检测、语义分割

OpenCV的DNN模块支持多种深度学习任务，包括图像分类、目标检测和语义分割。以下是一个简单的图像分类示例：

**图像分类**：

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
 
 int main() {
   // 加载预训练的Caffe模型
   cv::dnn::Net net = cv::dnn::readNetFromCaffe("deploy.prototxt", "model.caffemodel");
 
   // 加载图像
   cv::Mat image = cv::imread("image.jpg");
   if (image.empty()) {
     std::cerr << "Failed to load image!" << std::endl;
     return -1;
   }
 
   // 预处理图像
   cv::Mat blob = cv::dnn::blobFromImage(image, 1.0, cv::Size(224, 224), cv::Scalar(104, 117, 123));
 
   // 设置输入
   net.setInput(blob);
 
   // 前向传播
   cv::Mat prob = net.forward();
 
   // 获取分类结果
   cv::Point classIdPoint;
   double confidence;
   cv::minMaxLoc(prob.reshape(1, 1), 0, &confidence, 0, &classIdPoint);
   int classId = classIdPoint.x;
 
   std::cout << "Class ID: " << classId << ", Confidence: " << confidence << std::endl;
 
   return 0;
 }
```

以上代码中，我们加载了一个 Caffe 模型，并对输入图像进行分类。`cv::dnn::blobFromImage` 函数用于将图像转换为模型输入格式，`net.forward()` 用于执行前向传播，`cv::minMaxLoc` 用于获取分类结果。

#### 5.8.2.3 使用 OpenCV 运行 YOLOV5

OpenCV 的 DNN 模块还支持运行 YOLO（You Only Look Once）和SSD（Single Shot MultiBox Detector）等目标检测模型。

以下是一个使用 YOLOV5 模型进行目标检测的示例：

**YOLO目标检测：**

```c++
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>
#include <fstream>
#include <algorithm>

using namespace cv;       // OpenCV命名空间
using namespace dnn;      // OpenCV DNN模块命名空间
using namespace std;      // C++标准命名空间

// 初始化全局参数
float confThreshold = 0.5; // 置信度阈值，低于此值的检测结果将被丢弃
float nmsThreshold = 0.4;  // 非极大值抑制阈值，用于消除重叠框
int inputWidth = 640;      // 网络输入图像的宽度(YOLOv5通常使用640x640)
int inputHeight = 640;     // 网络输入图像的高度

vector<string> classes;    // 存储所有类别名称的容器

/**
 * @brief 加载类别名称文件
 * @param classesFile 包含类别名称的文本文件路径(如coco.names)
 */
void loadClasses(const string& classesFile) {
    ifstream ifs(classesFile.c_str());  // 创建文件输入流
    string line;
    while (getline(ifs, line)) {        // 逐行读取文件
        classes.push_back(line);         // 将每行内容(类别名称)添加到vector
    }
}

/**
 * @brief 在图像上绘制检测结果
 * @param classId 检测到的类别ID
 * @param conf 置信度分数
 * @param left 边界框左上角x坐标
 * @param top 边界框左上角y坐标
 * @param right 边界框右下角x坐标
 * @param bottom 边界框右下角y坐标
 * @param frame 要绘制的图像矩阵
 */
void drawPred(int classId, float conf, int left, int top, int right, int bottom, Mat& frame) {
    // 绘制矩形边界框
    rectangle(frame, Point(left, top), Point(right, bottom), Scalar(0, 255, 0), 2);
    
    // 格式化置信度为两位小数
    string label = format("%.2f", conf);
    
    // 如果有类别名称，添加到标签中
    if (classId >= 0 && classId < static_cast<int>(classes.size())) {
        label = classes[classId] + ": " + label;
    }
    
    // 计算标签文本的大小
    int baseLine;
    Size labelSize = getTextSize(label, FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseLine);
    
    // 确保标签不会超出图像顶部
    top = max(top, labelSize.height);
    
    // 在标签下方绘制背景矩形(提高可读性)
    rectangle(frame, Point(left, top - labelSize.height),
              Point(left + labelSize.width, top + baseLine), 
              Scalar(0, 255, 0), FILLED);
    
    // 在背景上绘制文本
    putText(frame, label, Point(left, top), 
            FONT_HERSHEY_SIMPLEX, 0.5, Scalar(0, 0, 0), 1);
}

/**
 * @brief 对网络输出进行后处理
 * @param frame 原始图像(用于获取尺寸)
 * @param outs 网络输出结果
 * 
 * 处理步骤:
 * 1. 过滤低置信度的检测
 * 2. 应用非极大值抑制(NMS)
 * 3. 绘制最终检测结果
 */
void postprocess(Mat& frame, const vector<Mat>& outs) {
    vector<int> classIds;
    vector<float> confidences;
    vector<Rect> boxes;
    const float sx = static_cast<float>(frame.cols) / inputWidth;
    const float sy = static_cast<float>(frame.rows) / inputHeight;
    // 适用 YOLOv5 v7.0 标准检测 ONNX：已解码、未内置 NMS，形状 [1,N,5+nc]。
    // 对应下文 blobFromImage 的直接缩放；letterbox 需要另行扣除 padding。
    for (const Mat& out : outs) {
        CV_Assert(out.type() == CV_32F && out.isContinuous());
        CV_Assert(out.dims == 3 && out.size[0] == 1 && out.size[2] > 5);
        const int rows = out.size[1], cols = out.size[2];
        const float* data = out.ptr<float>();
        for (int i = 0; i < rows; ++i, data += cols) {
            if (data[4] < confThreshold) continue;
            int classId = 0;
            float classScore = data[5];
            for (int c = 6; c < cols; ++c) {
                if (data[c] > classScore) { classScore = data[c]; classId = c - 5; }
            }
            const float confidence = data[4] * classScore;
            if (confidence < confThreshold) continue;
            // x,y,w,h 是网络输入尺寸上的像素坐标，不是归一化到 0~1 的坐标。
            const int left = cvRound((data[0] - data[2] / 2) * sx);
            const int top = cvRound((data[1] - data[3] / 2) * sy);
            Rect box(left, top, cvRound(data[2] * sx), cvRound(data[3] * sy));
            box &= Rect(0, 0, frame.cols, frame.rows);
            if (box.empty()) continue;
            boxes.push_back(box); classIds.push_back(classId); confidences.push_back(confidence);
        }
    }
    // 按类别执行 NMS，防止不同类别的重叠目标相互抑制。
    vector<int> visited;
    for (int cid : classIds) {
        if (std::find(visited.begin(), visited.end(), cid) != visited.end()) continue;
        visited.push_back(cid);
        vector<Rect> localBoxes;
        vector<float> localScores;
        vector<int> mapping, kept;
        for (size_t i = 0; i < boxes.size(); ++i) {
            if (classIds[i] == cid) {
                mapping.push_back(static_cast<int>(i));
                localBoxes.push_back(boxes[i]); localScores.push_back(confidences[i]);
            }
        }
        NMSBoxes(localBoxes, localScores, confThreshold, nmsThreshold, kept);
        for (int k : kept) {
            int idx = mapping[k]; const Rect& b = boxes[idx];
            drawPred(cid, confidences[idx], b.x, b.y, b.x + b.width, b.y + b.height, frame);
        }
    }
}



















































int main() {
    // 1. 加载类别名称文件
    string classesFile = "coco.names";
    loadClasses(classesFile);
    
    // 2. 加载YOLOv5 ONNX模型
    string modelPath = "yolov5s.onnx";
    Net net = readNet(modelPath);
    
    // 可选: 设置计算后端(使用CUDA加速)
    // net.setPreferableBackend(DNN_BACKEND_CUDA);
    // net.setPreferableTarget(DNN_TARGET_CUDA);
    
    // 3. 打开视频源(摄像头或视频文件)
    VideoCapture cap(0); // 0表示默认摄像头
    // VideoCapture cap("test.mp4"); // 使用视频文件
    
    if (!cap.isOpened()) {
        cerr << "无法打开视频源" << endl;
        return -1;
    }
    
    Mat frame, blob;
    
    // 4. 主循环: 处理每一帧
    while (waitKey(1) < 0) {
        // 读取一帧
        cap >> frame;
        if (frame.empty()) {
            break;  // 视频结束或读取失败
        }
        
        // 5. 图像预处理
        // 参数说明:
        // - 1./255.: 归一化到0-1范围
        // - Size(inputWidth, inputHeight): 调整大小
        // - Scalar(): 不进行均值减法
        // - true: 交换R和B通道(OpenCV使用BGR,YOLO通常需要RGB)
        // - false: 不裁剪图像
        blobFromImage(frame, blob, 1./255., Size(inputWidth, inputHeight), 
                     Scalar(), true, false);
        
        // 6. 设置网络输入
        net.setInput(blob);
        
        // 7. 前向传播(推理)
        vector<Mat> outs;
        net.forward(outs, net.getUnconnectedOutLayersNames());
        
        // 8. 后处理(解码输出、NMS、绘制结果)
        postprocess(frame, outs);
        
        // 9. 计算并显示推理时间
        vector<double> layersTimes;
        double freq = getTickFrequency() / 1000;  // 获取时钟频率并转换为毫秒
        double t = net.getPerfProfile(layersTimes) / freq;
        string label = format("Inference time: %.2f ms", t);
        putText(frame, label, Point(0, 15), FONT_HERSHEY_SIMPLEX, 0.5, Scalar(0, 0, 255));
        
        // 10. 显示结果
        imshow("YOLOv5 Object Detection", frame);
    }
    
    return 0;
}
```

以上示例通过 `cv::dnn::readNet` 加载 YOLOv5 ONNX。`readNetFromDarknet` 用于 Darknet 的 cfg/weights，不能混作 ONNX 加载接口。本例要求输出为 `[1,N,5+类别数]`，不适用于 YOLOv8/YOLO11、分割模型、RKNN 定制分支的多尺度原始输出或内置 NMS 的导出模型。直接拉伸图像是简化演示；使用 letterbox 时，需要保存缩放比例和补边量并在后处理中逆变换。

## 5.9 实战案例

### 5.9.1 实时人脸检测

实时人脸检测是计算机视觉中的一个重要应用。

OpenCV 提供了预训练的 Haar 级联分类器，可以用于检测图像或视频中的人脸。

**实现步骤:**

1. 加载 Haar 级联分类器模型。
2. 打开摄像头或视频文件。
3. 对每一帧进行人脸检测。
4. 绘制检测结果并显示。

```c++
#include <opencv2/opencv.hpp>
#include <iostream>
 
 using namespace cv;
 using namespace std;
 
 int main() {
   // 加载 Haar 级联分类器
   CascadeClassifier faceCascade;
   if (!faceCascade.load("haarcascade_frontalface_default.xml")) {
     cout << "错误：无法加载 Haar 级联分类器！" << endl;
     return -1;
   }
 
   // 打开摄像头
   VideoCapture cap(0);
   if (!cap.isOpened()) {
     cout << "错误：无法打开摄像头！" << endl;
     return -1;
   }
 
   // 实时检测人脸
   Mat frame;
   while (true) {
     cap >> frame;
     if (frame.empty()) break;
 
     // 转换为灰度图像
     Mat gray;
     cvtColor(frame, gray, COLOR_BGR2GRAY);
 
     // 检测人脸
     vector<Rect> faces;
     faceCascade.detectMultiScale(gray, faces, 1.1, 3, 0, Size(30, 30));
 
     // 绘制检测结果
     for (const auto& face : faces) {
       rectangle(frame, face, Scalar(0, 255, 0), 2);
     }
 
     // 显示结果
     imshow("Face Detection", frame);
 
     // 按下 ESC 键退出
     if (waitKey(30) == 27) break;
   }
 
   // 释放资源
   cap.release();
   destroyAllWindows();
 
   return 0;
 }
```

## 5.10 编译arm64的opencv

1. 安装cmake-gui

   ```shell
   sudo apt install cmake-gui
   ```

2. 运行cmake-gui

3. 配置opencv

   ![image-20260121150436549](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20260121150436549.png)

4. 选择opencv-3.4.13\platforms\linux\aarch64-gnu.toolchain.cmake

5. 确认安装路径和交叉编译器
6. make -j8
7. make install

---

[总目录](总目录.md) · [上一篇：RK开发板入门与交叉编译及NFS](4-RK%E5%BC%80%E5%8F%91%E6%9D%BF%E5%85%A5%E9%97%A8%E4%B8%8E%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%8F%8ANFS.md) · [下一篇：人工智能与边缘计算基础](6-%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E4%B8%8E%E8%BE%B9%E7%BC%98%E8%AE%A1%E7%AE%97%E5%9F%BA%E7%A1%80.md)
