## 使用串口进行输出
在FreeRTOS中使用串口进行输出是一种常见的调试和信息传递方式。下面是一个简单的示例，展示如何在FreeRTOS任务中使用串口输出"Hello, World!"。
### 重定向putc函数
首先，我们需要重定向`putc`函数，以便将输出发送到串口。假设我们使用的是STM32微控制器，并且已经配置好了USART外设。

```c
int fputc(int ch, FILE *f)
{
    // 等待直到发送缓冲区为空
    while (!(USART1->SR & USART_SR_TXE));
    // 发送字符
    USART1->DR = (ch & 0xFF);
    return ch;
}


/*或者者使用HAL库的方式*/
#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif /* __GNUC__ */
PUTCHAR_PROTOTYPE
{
  HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
  return ch;
}
```

### 使用默认的FreeRTOS任务输出
在freertos.c文件当的startDefaultTask函数加入
``` cpp
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for(;;)
  { printf("Hello FreeRTOS World!\r\n");
    // 控制LED亮
    if (HAL_GPIO_ReadPin(GPIOA, KEY_Pin) == GPIO_PIN_RESET) {
      HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
    } else {
      HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    }   
    osDelay(1);
  }
  /* USER CODE END StartDefaultTask */
}
```

### 为什么使用printf输出是线程不安全的？
在多任务环境下，多个任务可能会同时调用`printf`函数进行输出操作。如果没有适当的同步机制，可能会导致输出内容混乱或丢失，因为`printf`函数内部使用了共享资源（如缓冲区）。为了确保线程安全，可以使用互斥锁（mutex）来保护`printf`调用，确保同一时间只有一个任务能够执行输出操作。
