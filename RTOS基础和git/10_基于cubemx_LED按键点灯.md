## 原理图讲解

### key和LED的说明
![key](embedded-development-note-main/RTOS基础和git/image-8.png)
>默认情况下，key没有被按下，现在的电平就是浮空状态，按下的时候，电平变为低电平(GND)

![LED](embedded-development-note-main/RTOS基础和git/image-9.png)
>PC13 这里只要输出低电平，LED就会点亮，输出高电平，LED熄灭
 下边的PWR_LED是电源指示灯，常亮(输出高电平)

## 使用CubeMX配置定时器实现LED按键控制(裸机)
![alt text](embedded-development-note-main/RTOS基础和git/image-10.png)
>Debug 这里选中Serial Wire Viewer (SWV) ITM Data Console

![时钟配置](embedded-development-note-main/RTOS基础和git/image-11.png)
> 这里要和外部的原理图匹配

__根据刚才的原理图，我们知道LED接在PC13口，所以我们要把PC13口配置成GPIO_Output模式,还有key是PA0，需要变成GPIO_Input模式__
![alt text](embedded-development-note-main/RTOS基础和git/image-12.png)

### 下载

![alt text](embedded-development-note-main/RTOS基础和git/image-13.png)
__进入Debug模式，选择SWD接口，点击下载按钮即可把代码下载到MCU中__

### 代码控制延时和闪烁
GPIO的初始化
``` cpp
/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    gpio.c
  * @brief   This file provides code for the configuration
  *          of all used GPIO pins.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "gpio.h"

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/*----------------------------------------------------------------------------*/
/* Configure GPIO                                                             */
/*----------------------------------------------------------------------------*/
/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

/** Configure pins as
        * Analog
        * Input
        * Output
        * EVENT_OUT
        * EXTI
*/
void MX_GPIO_Init(void)
{

  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : PtPin */
  GPIO_InitStruct.Pin = KEY_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(KEY_GPIO_Port, &GPIO_InitStruct);

}

/* USER CODE BEGIN 2 */

/* USER CODE END 2 */
```
在main 函数当中
``` cpp     
nt main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
    HAL_Delay(500);
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);//LED toggle every 500ms翻转
    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}
```
这里使用了HAL库提供的`HAL_Delay()`函数来实现延时，`HAL_GPIO_TogglePin()`函数来翻转LED的状态。

### 按键控制LED
在while循环中添加按键检测代码
``` cpp
while(1)
{
    if(HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin) == GPIO_PIN_RESET) //检测按键是否按下
    {
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin); //翻转LED状态
        HAL_Delay(200); //消抖延时
    }
    HAL_Delay(50); //主循环延时
}
``` 

## 总结
>本章节我们学习了如何使用CubeMX配置STM32的GPIO引脚，实现LED的闪烁和按键控制功能。通过实际操作，我们掌握了CubeMX的基本使用方法以及HAL库的GPIO操作函数，为后续的嵌入式开发打下了基础。

### 基于单击和长安击实现不同的LED控制
在写代码的之前一定要明确写代码的逻辑，可以在`function`函数头上加入note，方便自己理解
ex:
- 1.使用scan函数判断按键状态
- 2.使用计时器函数计算按键按下的时间
- 3.根据按下时间的长短决定执行单击还是长按操作

根据不同的工程师分工，这里就可以分成`bsp`和`application`两个层次来写代码
- bsp工程师写按键扫描和计时器函数
- application工程师写单击和长按的逻辑处理（调用bsp的函数 设计timer的时长）