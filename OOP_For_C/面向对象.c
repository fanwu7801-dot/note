#include <stdio.h>

int add (int a, int b) {
    return a + b;
}
int sum (int a, int b) {
    return a - b;
}

/*main函数当中声明函数指针*/
int main()
{
    int (*p)(int , int );  /*声明一个函数指针p，指向函数，函数的参数为两个int类型，返回值为int类型*/
    p = add;               /*让函数指针p指向add函数*/
    int result = p(3,4);  /*通过函数指针调用add函数*/
    printf("result = %d\n",result);
    /*实现动态绑定*/
    p = sum;              /*让函数指针p指向sum函数*/
    result = p(3,4);      /*通过函数指针调用sum函数*/
    printf("result = %d\n",result);

    return 0;
}