# C 语言指针强化教程

## 1. 指针是什么

普通变量保存数据，指针变量保存地址：

```c
int value = 10;
int *pointer = &value;
```

`&value` 表示取地址，`*pointer` 表示访问该地址中的数据。
执行 `*pointer = 20;` 后，`value` 也会变成 `20`。

指针类型决定解引用时读取多少字节，也决定指针加一时移动多少字节。

## 2. 我的指针思考方法

学习指针时，不要先背复杂声明。每次看到一个指针，都先问三个问题：

1. 变量本身是什么类型，是普通变量、数组，还是指针？
2. 它保存的是一个值，还是另一个对象的地址？
3. 解引用后访问的对象是否仍然有效，范围是否正确？

阅读复杂声明时，从变量名开始向外读。例如：

```c
int *pointer_array[3];
int (*array_pointer)[3];
```

第一行中，变量名 `pointer_array` 先和 `[3]` 结合，所以它是数组；数组
中的每个元素再和 `*` 结合，因此每个元素都是 `int *`，这叫指针数组。
第二行中，括号让变量名先和 `*` 结合，所以它是指针；这个指针再和
`[3]` 结合，因此它指向一个包含 3 个 `int` 的数组，这叫数组指针。

可以用一句话记忆：

```text
int *p[3]       p 是数组，数组元素是指针
int (*p)[3]     p 是指针，指向一个数组
```

判断时，括号是关键。没有括号时，数组下标 `[]` 的结合优先级高于指针
解引用 `*`。

## 3. 数组作为参数时会退化

数组在表达式中通常会转换为指向首元素的指针，这个过程常被称为“数组
退化”。例如：

```c
void PrintArray(const int *array, size_t length)
{
    size_t index;

    if (NULL == array)
    {
        return;
    }

    for (index = 0U; index < length; index++)
    {
        printf("%d ", array[index]);
    }
}
```

调用 `PrintArray(numbers, 3U)` 时，传入的不是整个数组的副本，而是首
元素 `numbers[0]` 的地址。因此函数内部无法仅靠 `array` 得到元素个数，
必须额外传入 `length`。

下面这个例外很重要：数组作为 `sizeof` 的操作数时不会退化：

```c
int numbers[3] = {10, 20, 30};

sizeof(numbers);       /* 整个数组的大小 */
sizeof(&numbers[0]);   /* 首元素指针的大小 */
```

二维数组传参时，第一维可以省略，但列数不能省略，因为编译器需要通过
列数计算下一行的地址：

```c
void PrintMatrix(const int matrix[][3], size_t rows);
```

这个参数本质上等价于 `const int (*matrix)[3]`，也就是数组指针。这里
只发生第一维的退化，每个元素仍然是一行包含 3 个 `int` 的数组。

## 4. 初始化与空指针

```c
int number = 10;
int *pointer = &number;
int *empty = NULL;

if (NULL != pointer)
{
    *pointer = 30;
}
```

未初始化的指针是野指针，不能直接解引用。`NULL` 也不能解引用，
使用前必须检查。

## 5. 指针与数组

数组名在多数表达式中会转换为首元素地址：

```c
int numbers[3] = {10, 20, 30};
int *pointer = numbers;

numbers[1];       /* 20 */
*(numbers + 1);   /* 20 */
pointer[1];       /* 20 */
*(pointer + 1);   /* 20 */
```

数组和指针不是同一种对象。`sizeof(numbers)` 得到整个数组大小，
`sizeof(pointer)` 得到指针变量自身的大小。访问不能越过数组边界。

## 6. 指针数组与数组指针

读声明时，从变量名向外读，再结合括号：

```c
int *pointer_array[3];
```

这是“长度为 3 的数组，每个元素都是 `int *`”，即指针数组：

```c
int first = 10;
int second = 20;
int *pointer_array[2] = {&first, &second};

printf("%d\n", *pointer_array[1]);
```

```c
int (*array_pointer)[3];
```

这是“一个指针，指向包含 3 个 `int` 的数组”，即数组指针：

```c
int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
int (*array_pointer)[3] = matrix;

printf("%d\n", array_pointer[1][2]);
```

`int *p[3]` 中 `p` 先与 `[]` 结合，所以 `p` 是数组；
`int (*p)[3]` 中括号使 `p` 先与 `*` 结合，所以 `p` 是指针。

## 7. 二维数组传参

二维数组作为函数参数时，必须保留列数：

```c
void PrintMatrix(const int (*matrix)[3], size_t rows)
{
    size_t row;
    size_t column;

    if (NULL == matrix)
    {
        return;
    }

    for (row = 0U; row < rows; row++)
    {
        for (column = 0U; column < 3U; column++)
        {
            printf("%d ", matrix[row][column]);
        }
        printf("\n");
    }
}
```

`const int matrix[][3]` 与上面的参数本质相同。列数用于计算下一行的
起始地址，行数需要由调用者额外传入。

## 8. 指针作为函数参数

C 语言参数是值传递。要修改调用者的变量，必须传入地址：

```c
void Swap(int *left, int *right)
{
    int temporary;

    if ((NULL == left) || (NULL == right))
    {
        return;
    }

    temporary = *left;
    *left = *right;
    *right = temporary;
}
```

数组参数通常还要传入长度，因为函数收到的是首元素指针。

```c
int Sum(const int *array, size_t length)
{
    int result = 0;
    size_t index;

    if (NULL == array)
    {
        return 0;
    }

    for (index = 0U; index < length; index++)
    {
        result += array[index];
    }

    return result;
}
```

## 9. `const` 与指针

```c
const int *p1;       /* 不能通过 p1 修改目标数据 */
int *const p2 = &x;  /* p2 不能改指向，但可以修改目标数据 */
const int *const p3 = &x; /* 两者都不能通过 p3 修改 */
```

只读函数参数通常写成 `const char *text`，表示函数不会通过该指针修改
字符串内容。

## 10. 字符串与字符指针

字符串是以 `\\0` 结尾的字符数组：

```c
char text[] = "hello";
char *pointer = text;

while ('\\0' != *pointer)
{
    printf("%c\\n", *pointer);
    pointer++;
}
```

`char writable[] = "hello"` 的数组内容可以修改；
`const char *read_only = "hello"` 指向字符串常量，不应修改。

## 11. 二级指针

指针本身也有地址，因此可以使用二级指针：

```c
int value = 10;
int *pointer = &value;
int **double_pointer = &pointer;

printf("%d\\n", **double_pointer);
```

二级指针常用于函数修改调用者的指针，例如动态申请内存：

```c
#include <stdlib.h>

int CreateValue(int **result)
{
    if (NULL == result)
    {
        return 0;
    }

    *result = malloc(sizeof(**result));
    if (NULL == *result)
    {
        return 0;
    }

    **result = 100;
    return 1;
}
```

## 12. 结构体指针

结构体指针使用 `->` 访问成员：

```c
typedef struct
{
    int speed;
    int temperature;
} VehicleData;

VehicleData data = {60, 25};
VehicleData *pointer = &data;

pointer->speed = 80;
```

`pointer->speed` 与 `(*pointer).speed` 等价。

## 13. 函数指针与函数指针数组

```c
typedef int (*Operation)(int, int);

int Add(int left, int right)
{
    return left + right;
}

int Subtract(int left, int right)
{
    return left - right;
}

Operation operations[2] = {Add, Subtract};
int result = operations[1](8, 3);
```

`operations` 是函数指针数组，适合实现命令表和状态处理表。使用前应
保证函数签名完全匹配，并检查可能为空的函数指针。

## 14. 动态内存

```c
#include <stdlib.h>

int *array = malloc(5U * sizeof(*array));

if (NULL != array)
{
    array[0] = 10;
    free(array);
    array = NULL;
}
```

必须检查申请结果，确保每块内存只释放一次；释放后不能继续访问，也不应
返回局部变量的地址。

## 15. 常见错误

```c
int *pointer;
*pointer = 10;       /* 未初始化的野指针 */
```

```c
int array[3];
array[3] = 10;       /* 越界，下标范围是 0 到 2 */
```

```c
int *pointer = malloc(sizeof(*pointer));
free(pointer);
*pointer = 10;       /* 释放后继续使用 */
```

```c
int *GetAddress(void)
{
    int local = 10;
    return &local;   /* 返回已失效的局部变量地址 */
}
```

## 16. 练习题

1. 编写带空指针检查的 `Swap` 函数，交换两个整数。
2. 使用 `const int *array` 和长度求数组最大值。
3. 解释 `int *a[4]` 与 `int (*b)[4]`，并分别访问元素。
4. 编写接收 `int matrix[][4]` 的函数，计算二维数组总和。
5. 使用函数指针数组实现加法、减法和乘法的命令分发。

## 17. 使用指针前的自检

1. 指针是否已初始化并指向有效对象？
2. 是否可能为 `NULL`？
3. 对象是否仍在生命周期内？
4. 访问是否在合法范围内？
5. `const` 是否正确表达读写权限？
6. 动态内存是否有明确且唯一的释放责任？
7. 指针类型是否与目标对象类型匹配？

理解指针时，始终确认指针变量本身的位置、它保存的地址，以及该地址
对应对象的生命周期和访问范围。
