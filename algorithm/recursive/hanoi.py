# -*- coding: utf-8 -*-


c = 0
def hanoi(n, x, y, z):
    global c
    # if n == 1:
        # print("%s --> %s" % (x, y))
    if n >= 1:
        hanoi(n-1, x, z, y)
        print("%s: %s --> %s" % (c, x, y))
        c += 1
        hanoi(n-1, z, y, x)


if __name__ == "__main__":
    hanoi(3, 'x', 'y', 'z')
