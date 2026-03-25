#include <stdio.h>
#include <stdint.h>
#include <string.h>  // 用于memset

// 假设的串口发送函数（模拟）
void uart_send(uint8_t* data, size_t len) {
    printf("发送数据: ");
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

// 定义结构体（使用packed避免填充）
typedef struct __attribute__((packed)) {
    uint8_t id;
    uint16_t value;
    uint32_t timestamp;
} sensor_data_t;

int main() {
    sensor_data_t data;

    // 情况1: 未初始化成员（危险！）
    printf("=== 未初始化结构体 ===\n");
    printf("id: %d, value: %d, timestamp: %u\n", data.id, data.value, data.timestamp);
    uart_send((uint8_t*)&data, sizeof(sensor_data_t));

    // 情况2: 部分初始化
    printf("\n=== 部分初始化结构体 ===\n");
    data.id = 1;  // 只初始化id
    // value和timestamp未初始化
    printf("id: %d, value: %d, timestamp: %u\n", data.id, data.value, data.timestamp);
    uart_send((uint8_t*)&data, sizeof(sensor_data_t));

    // 情况3: 完全初始化（推荐）
    printf("\n=== 完全初始化结构体 ===\n");
    data.id = 1;
    data.value = 1234;
    data.timestamp = 567890;
    printf("id: %d, value: %d, timestamp: %u\n", data.id, data.value, data.timestamp);
    uart_send((uint8_t*)&data, sizeof(sensor_data_t));

    // 情况4: 使用memset清零后初始化
    printf("\n=== memset清零后初始化 ===\n");
    memset(&data, 0, sizeof(sensor_data_t));  // 清零所有成员
    data.id = 2;
    data.value = 5678;
    printf("id: %d, value: %d, timestamp: %u\n", data.id, data.value, data.timestamp);
    uart_send((uint8_t*)&data, sizeof(sensor_data_t));

    return 0;
}