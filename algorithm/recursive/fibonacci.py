# -*- coding: utf-8 -*-


def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n > 1:
        data = fibonacci(n-1) + fibonacci(n-2)
        return data


def fibonacci_sum(n):
    accu = 0
    for i in range(n):
        accu += fibonacci(i)
    return accu

if __name__ == "__main__":
    data = fibonacci(5)
    print data

    sum_data = fibonacci_sum(5)
    print sum_data


