import os
from typing import TypeVar, Union, List, Type, Tuple, Any
import yaml
import json
import re
import multiprocessing as mp
import requests
import time
import platform


def write_config():
    with open("config.yaml", "w", encoding="utf-8") as f:
        f.write("page_size: 10\nmax_process: 5\nmusic_dir: '../music/'\nsave_artist: true")


def read_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


if os.path.exists("config.yaml"):
    CONFIG = read_config()
else:
    write_config()
    CONFIG = read_config()
try:
    PAGE_SIZE = CONFIG["page_size"]  # 每页显示的数量
    MAX_PROCESS = CONFIG["max_process"]  # 最大进程数
    MUSIC_DIR = CONFIG["music_dir"]  # 音乐文件保存路径
    SAVE_ARTIST = CONFIG["save_artist"]     # 文件名中是否含有艺术家信息
except KeyError:
    write_config()
    PAGE_SIZE = 10
    MAX_PROCESS = 5
    MUSIC_DIR = "music/"
    SAVE_ARTIST = True

T = TypeVar("T")
StrInt = Union[str, int]
COLOR_DICT = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35, "cyan": 36, "white": 37}
# 判断当前系统是否支持彩色输出
system_type = platform.system()
if system_type == 'Windows':
    windows_version = float(platform.win32_ver()[0])
    if windows_version >= 10:
        COLORFUL_OK = True
    else:
        COLORFUL_OK = False
elif system_type == 'Linux':
    COLORFUL_OK = True
else:
    COLORFUL_OK = False
# 如果当前文件夹下没有music文件夹，则创建一个
if not os.path.exists(MUSIC_DIR):
    os.mkdir(MUSIC_DIR)


def colorful(s: str,
             color: str = "default",
             highlight: bool = False) -> str:
    """
    输出彩色字符
    :param s: 字符串
    :param color: 颜色
    :param highlight: 是否高亮
    :return: 变了颜色的字符串
    """
    try:
        assert color in ["default", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    except AssertionError:
        my_print("[Warning] 颜色必须是以下颜色之一: None, 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'！已默认为白色。", "yellow")
        return s
    if not COLORFUL_OK:
        return s
    highlight = 1 if highlight else 0
    if color == "default":
        return s
    else:
        return f"\033[{highlight};{COLOR_DICT[color]}m{s}\033[m"


def my_print(s: str,
             *args,
             sep=' ',
             end='\n',
             file=None,
             color: str = "default",
             highlight: bool = False,
             ) -> None:
    """
    自定义输出，可以输出彩色字符
    :param s: 字符串
    :param args: 其他参数
    :param sep: 分隔符
    :param end: 结尾字符
    :param file: 文件
    :param color: 颜色（默认default白色输出；红色：red；绿色：green；黄色：yellow；蓝色：blue；品红：magenta；青色：cyan；白色：white）
    :param highlight: 是否高光
    :return: None
    """
    print(colorful(s, color, highlight), *args, sep=sep, end=end, file=file)


def my_input(prompt: str = "",
             t: Type[T] = str,
             color: str = "default",
             highlight: bool = False,
             min_val: Union[int, float] = 0,
             max_val: Union[int, float] = 0,
             default: Any = '') -> T:
    """
    自定义输入函数
    :param prompt: 提示符
    :param t: 输入后得到的类型
    :param color: 提示颜色
    :param highlight: 是否高亮
    :param min_val: 如果期望得到一个数字，这个用来限定数值范围最小值
    :param max_val: 如果期望得到一个数字，这个用来限定数值范围最大值
    :param default: 默认值
    :return: 任意类型
    """
    while True:
        ret = input(colorful(prompt, color, highlight))
        if t is str:
            break
        if ret == "":
            return default
        try:
            ret = t(ret)
        except NameError:
            my_print("[Warning] 输入函数传参时指定的类型不错误！已默认为str。", color="yellow", highlight=True)
            break
        except ValueError:
            my_print(f"[Error] 输入的类型限制为{t}，请重新输入！", color="red", highlight=True)
            continue
        if t is int or t is float:
            if min_val <= ret <= max_val:
                break
            else:
                my_print(f"[Error] 输入的数值范围应当在{min_val}~{max_val}，请重新输入！", color="red", highlight=True)
                continue
        else:
            break
    return ret


def print_query(ls: Union[List[Tuple[StrInt, str, str]], List[Tuple[StrInt, str, str, StrInt, str]]],
                page: int = 0,
                no_album: bool = False) -> None:
    """
    输出一个查询结果
    :param ls: 查询结果列表
    :param page: 当前页号
    :param no_album: 是否不输出专辑信息
    :return: None
    """
    page_size = len(ls)
    if no_album:
        # 没有专辑的情况下，列表结构为[[歌曲序号, 歌曲名称, 艺术家], ...]
        my_print("选择歌曲", color="green", highlight=True, end="\t")
        my_print("歌曲名称", end="\t")
        my_print("艺术家", color="red")
        for idx, music_info in enumerate(ls):
            my_print(f"[{idx + 1}]", color="green", highlight=True, end="\t")
            my_print(music_info[1], end="\t")
            my_print(f"{music_info[2]}", color="red")
    else:
        # 有专辑的情况下，列表结构为[[歌曲序号, 歌曲名称, 艺术家, 专辑序号, 专辑名称], ...]
        my_print("选择歌曲", color="green", highlight=True, end="\t")
        my_print("选择专辑", color="blue", highlight=True, end="\t")
        my_print("歌曲名称", end="\t")
        my_print("艺术家", color="red", end="\t")
        my_print("专辑名称", color="yellow")
        for idx, music_info in enumerate(ls):
            my_print(f"[{idx + 1}]", color="green", highlight=True, end="\t")
            my_print(f"[{idx + page_size + 1}]", color="blue", highlight=True, end="\t")
            my_print(f"{music_info[1]}", end="\t")
            my_print(f"{music_info[2]}", color="red", end="\t")
            my_print(f"{music_info[4]}", color="yellow")
    my_print(f"当前页面：{page}", color="magenta", highlight=True)
    my_print("[0]返回搜索", color="red", highlight=True, end="\t")
    options_count = page_size if no_album else 2 * page_size
    my_print(f"[{options_count + 1}]上一页", color="yellow", highlight=True, end="\t")
    my_print(f"[{options_count + 2}]下一页", color="green", highlight=True)


def print_album(ls: list,
                album_name: str,
                album_artist_name: str) -> None:
    """
    打印专辑信息
    :param ls: 专辑信息列表
    :param album_name: 专辑名称
    :param album_artist_name: 艺术家名称
    :return: None
    """
    my_print(f"专辑名称：{album_name}", color="yellow", highlight=True, end="\t")
    my_print(f"艺术家：{album_artist_name}", color="red", highlight=True)
    my_print("歌曲序号", color="green", highlight=True, end="\t")
    my_print("歌曲名称")
    music_cnt = len(ls)
    for idx, music_info in enumerate(ls):
        my_print(f"[{idx + 1}]", color="green", highlight=True, end="\t")
        my_print(music_info[1])
    my_print("[0]返回搜索", color="red", highlight=True, end="\t")
    my_print(f"[{music_cnt + 1}]下载全部", color="green", highlight=True)


def print_song_list(ls: list,
                    song_list_name: str,
                    song_list_creator: str) -> None:
    """
    打印歌单信息
    :param ls: 歌单信息列表
    :param song_list_name: 歌单名称
    :param song_list_creator: 歌单创建者名称
    :return: None
    """
    page_size = len(ls)
    my_print(f"歌单名称：{song_list_name}", color="yellow", highlight=True, end="\t")
    my_print(f"创建者：{song_list_creator}", color="red", highlight=True)
    my_print("选择歌曲", color="green", highlight=True, end="\t")
    my_print("选择专辑", color="blue", highlight=True, end="\t")
    my_print("歌曲名称", end="\t")
    my_print("艺术家", color="red", end="\t")
    my_print("专辑名称", color="yellow")
    for idx, music_info in enumerate(ls):
        my_print(f"[{idx + 1}]", color="green", highlight=True, end="\t")
        my_print(f"[{idx + page_size + 1}]", color="blue", highlight=True, end="\t")
        my_print(f"{music_info[1]}", end="\t")
        my_print(f"{music_info[2]}", color="red", end="\t")
        my_print(f"{music_info[4]}", color="yellow")
    my_print("[0]返回搜索", color="red", highlight=True, end="\t")
    my_print(f"[{page_size * 2 + 1}]下载全部", color="green", highlight=True)


def clear_screen() -> None:
    """清屏"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def get_parameter_value(url, param_name) -> str:
    """
    获取url中的参数值
    :param url:
    :param param_name:
    :return:
    """
    index = url.find("?")
    url = url[index + 1:]
    param_value = url.split("&")
    param_value = [param.split("=") for param in param_value]
    param_value = [value[1] for value in param_value if value[0] == param_name]
    if param_value:
        return param_value[0]
    else:
        return ''
