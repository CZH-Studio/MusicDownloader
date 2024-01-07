from utils import *
import netease
import qq
import kugou
import bilibili


def input_int(min_val: int, max_val: int, prompt="请输入操作序号：") -> int:
    while True:
        choice = input(prompt)
        try:
            choice = int(choice)
            if choice < min_val or choice > max_val:
                print(f"\033[1;31m[Error] 输入的数值范围在{min_val}~{max_val}。\033[m")
                continue
            else:
                return choice
        except ValueError:
            print("\033[1;31m[Error] 请输入一个数字。\033[m")
            continue


def print_platform():
    print("\033[1;32m选择平台\033[m", end='\t')
    print("平台名称")
    print("\033[1;32m[1]\033[m", end='\t')
    print("网易云音乐")
    print("\033[1;32m[2]\033[m", end='\t')
    print("QQ音乐")
    print("\033[1;32m[3]\033[m", end='\t')
    print("酷狗音乐")
    print("\033[1;32m[4]\033[m", end='\t')
    print("哔哩哔哩")
    print("\033[1;31m[0]\t退出程序\033[m")


def main():
    while True:
        print_platform()
        choice = input_int(0, 7,  prompt="请选择一个音乐平台：")
        clear_screen()
        if choice == 0:
            break
        elif choice == 1:
            netease.main()
        elif choice == 2:
            qq.main()
        elif choice == 3:
            kugou.main()
        elif choice == 4:
            bilibili.main()


if __name__ == '__main__':
    main()
