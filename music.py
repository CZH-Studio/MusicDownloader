from utils import *
import kugou
import bilibili
import netease
import qq


def print_platform():
    my_print("选择平台", color="green", highlight=True, end='\t')
    my_print("平台名称")
    my_print("[1]", color="green", highlight=True, end='\t')
    my_print("网易云音乐")
    my_print("[2]", color="green", highlight=True, end='\t')
    my_print("QQ音乐")
    my_print("[3]", color="green", highlight=True, end='\t')
    my_print("酷狗音乐")
    my_print("[4]", color="green", highlight=True, end='\t')
    my_print("哔哩哔哩")
    my_print("[0]\t退出程序", color="red", highlight=True)


def main():
    while True:
        print_platform()
        choice = my_input("请选择一个音乐平台([0]~4)：", int, min_val=0, max_val=4, default=0)
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
