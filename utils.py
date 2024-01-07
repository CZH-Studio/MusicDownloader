import os


PAGE_SIZE = 10


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


def print_query(ls: list, page=0):
    page_size = len(ls)
    print("\033[1;32m选择歌曲\033[m", end="\t")
    print("\033[1;34m选择专辑\033[m", end="\t")
    print("歌曲名称", end="\t")
    print("\033[0;31m艺术家\033[m", end="\t")
    print("\033[0;33m专辑名称\033[m")
    for idx, music_info in enumerate(ls):
        print(f"\033[1;32m[{idx+1}]\033[m", end="\t")
        print(f"\033[1;34m[{idx+page_size+1}]\033[m", end="\t")
        print(f"{music_info[2]}", end="\t")
        print(f"\033[0;31m{music_info[3]}\033[m", end="\t")
        print(f"\033[0;33m{music_info[4]}\033[m")
    print(f"当前页面：{page}", end="\t")
    print("\033[1;31m[0]返回搜索\033[m", end="\t")
    print(f"\033[1;33m[{2*page_size+1}]上一页\033[m", end="\t")
    print(f"\033[1;32m[{2*page_size+2}]下一页\033[m")


def print_album(ls: list, key_name: str, album_name: str, album_artist_name: str):
    print(f"\033[1;33m专辑名称：{album_name}\033[m", end="\t")
    print(f"\033[1;31m艺术家：{album_artist_name}\033[m")
    print("\033[1;32m选择歌曲\033[m", end="\t")
    print("歌曲名称")
    music_cnt = len(ls)
    for idx, music_info in enumerate(ls):
        print(f"\033[1;32m[{idx + 1}]\033[m", end="\t")
        print(music_info[key_name])
    print("\033[1;31m[0]返回\033[m", end="\t")
    print(f"\033[1;33m[{music_cnt + 1}]下载专辑\033[m")


def print_names(ls: list, page=0):
    page_size = len(ls)
    print("\033[1;32m选择歌曲\033[m", end="\t")
    print("歌曲名称", end="\t")
    print("\033[0;31mUP主\033[m")
    for idx, music_info in enumerate(ls):
        print(f"\033[1;32m[{idx + 1}]\033[m", end="\t")
        print(music_info[1], end="\t")
        print(f"\033[0;31m{music_info[2]}\033[m")
    print(f"当前页面：{page}", end="\t")
    print("\033[1;31m[0]返回搜索\033[m", end="\t")
    print(f"\033[1;33m[{page_size + 1}]上一页\033[m", end="\t")
    print(f"\033[1;32m[{page_size + 2}]下一页\033[m")


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
