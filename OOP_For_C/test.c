#include <stdio.h>
#include <stdlib.h>

// 面向对象思想在C语言中的实现：通过结构体封装数据和行为，函数指针模拟方法
// 这体现了封装：数据和操作绑定在一起；多态：不同类型有不同实现

// 定义LED状态枚举（模拟面向对象的属性）
typedef enum {
    LED_OFF = 0,
    LED_ON = 1
} led_state_t;

// 定义LED类型枚举（用于多态实现）
typedef enum {
    LED_TYPE_GPIO,
    LED_TYPE_PWM
} led_type_t;

// LED设备结构体（模拟类）：封装属性和方法
typedef struct led_device {
    // 属性成员（数据封装）
    led_state_t state;     // 当前状态
    led_type_t type;       // 设备类型（用于多态）

    // 方法成员（函数指针模拟方法）
    // 初始化设备（构造函数）
    struct led_device* (*init)(struct led_device* dev);
    // 反初始化设备（析构函数）
    void (*deinit)(struct led_device* dev);
    // 获取状态
    led_state_t (*get_state)(struct led_device* dev);
    // 设置状态
    void (*set_state)(struct led_device* dev, led_state_t state);
} led_device_t;

// GPIO类型LED的获取状态实现（多态的具体实现）
static led_state_t gpio_get_state(led_device_t* dev) {
    printf("GPIO LED: 读取硬件GPIO引脚状态\n");
    return dev->state;  // 模拟读取硬件
}

// GPIO类型LED的设置状态实现
static void gpio_set_state(led_device_t* dev, led_state_t state) {
    dev->state = state;
    printf("GPIO LED: 设置GPIO引脚为 %s\n", state ? "ON" : "OFF");
}

// PWM类型LED的获取状态实现（多态：不同行为）
static led_state_t pwm_get_state(led_device_t* dev) {
    printf("PWM LED: 读取PWM占空比状态\n");
    return dev->state;  // 模拟读取PWM值
}

// PWM类型LED的设置状态实现
static void pwm_set_state(led_device_t* dev, led_state_t state) {
    dev->state = state;
    printf("PWM LED: 设置PWM占空比为 %s\n", state ? "100%" : "0%");
}

// 初始化函数（模拟构造函数）
static led_device_t* led_init(led_device_t* dev) {
    if (dev->type == LED_TYPE_GPIO) {
        // 为GPIO类型绑定具体方法（多态）
        dev->get_state = gpio_get_state;
        dev->set_state = gpio_set_state;
    } else if (dev->type == LED_TYPE_PWM) {
        // 为PWM类型绑定具体方法
        dev->get_state = pwm_get_state;
        dev->set_state = pwm_set_state;
    }
    dev->state = LED_OFF;  // 默认状态
    printf("LED设备初始化完成，类型: %s\n",
           dev->type == LED_TYPE_GPIO ? "GPIO" : "PWM");
    return dev;
}

// 反初始化函数（模拟析构函数）
static void led_deinit(led_device_t* dev) {
    printf("LED设备反初始化\n");
    // 这里可以释放资源
}

// 主函数：演示面向对象的使用
int main() {
    printf("=== C语言模拟面向对象：LED设备管理 ===\n\n");

    // 创建GPIO LED实例（模拟对象实例化）
    led_device_t gpio_led = {
        .type = LED_TYPE_GPIO,
        .init = led_init,
        .deinit = led_deinit
    };

    // 创建PWM LED实例
    led_device_t pwm_led = {
        .type = LED_TYPE_PWM,
        .init = led_init,
        .deinit = led_deinit
    };

    // 初始化设备（调用构造函数）
    gpio_led.init(&gpio_led);
    pwm_led.init(&pwm_led);

    printf("\n--- 演示多态：相同接口，不同实现 ---\n");

    // 使用GPIO LED（多态：接口统一，行为不同）
    printf("操作GPIO LED:\n");
    gpio_led.set_state(&gpio_led, LED_ON);
    printf("当前状态: %s\n", gpio_led.get_state(&gpio_led) ? "ON" : "OFF");

    // 使用PWM LED（多态体现）
    printf("\n操作PWM LED:\n");
    pwm_led.set_state(&pwm_led, LED_ON);
    printf("当前状态: %s\n", pwm_led.get_state(&pwm_led) ? "ON" : "OFF");

    // 反初始化（调用析构函数）
    gpio_led.deinit(&gpio_led);
    pwm_led.deinit(&pwm_led);

    printf("\n=== 面向对象概念总结 ===\n");
    printf("封装: 数据(state,type)和行为(init,set_state等)绑定在结构体中\n");
    printf("多态: 相同接口(get_state,set_state)，不同类型(GPIO/PWM)有不同实现\n");
    printf("抽象: 通过函数指针定义接口，隐藏具体实现细节\n");
    printf("继承: 这里没有直接继承，但可以通过嵌套结构体实现\n");

    return 0;
}