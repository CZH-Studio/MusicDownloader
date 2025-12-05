from dataclasses import dataclass, asdict
from pathlib import Path
import os
import json
import queue
import threading
import textwrap

import requests
from prettytable import PrettyTable, PLAIN_COLUMNS

from music_platform import MusicPlatform, MusicQueryResult, Music


@dataclass
class Config:
    page_size: int = 10
    num_threads: int = 4
    save_dir: str = "music"
    save_filename: str = "{name} - {artist}"
    shorten: int = 20


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        config = Config()
        json.dump(asdict(config), open(CONFIG_PATH, "w"), indent=4)
    else:
        config = Config(**json.load(open(CONFIG_PATH)))
    Path(config.save_dir).mkdir(exist_ok=True, parents=True)
    return config


def cls() -> None:
    """清屏"""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def input_int(
    prompt: str,
    min_val: int | None = None,
    max_val: int | None = None,
    default: int | None = None,
) -> int:
    prompt_min = "" if min_val is None else str(min_val)
    prompt_max = "" if max_val is None else str(max_val)
    prompt_default = "" if default is None else f"[{default}]"
    if prompt_min or prompt_max:
        prompt_range = f" ({prompt_min}~{prompt_max} {prompt_default}): "
    elif prompt_default:
        prompt_range = f" ({prompt_default}): "
    else:
        prompt_range = ": "
    prompt = prompt + prompt_range
    while True:
        user_input = input(prompt)
        if user_input == "" and default is not None:
            return default
        try:
            num = int(user_input)
            if (min_val is None or num >= min_val) and (
                max_val is None or num <= max_val
            ):
                return num
            else:
                continue
        except ValueError:
            continue


def download_worker(thread_id: int):
    while not STOP_FLAG:
        try:
            music, url, headers, cookies, path = DOWNLOAD_QUEUE.get(timeout=1)
            music: Music
            url: str
            headers: dict
            cookies: dict
            path: Path
        except queue.Empty:
            continue
        try:
            response = requests.get(url, stream=True, headers=headers, cookies=cookies)
            response.raise_for_status()
            path.parent.mkdir(exist_ok=True, parents=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"{music.name} - {music.artists_str} 下载完成")
        except Exception as e:
            print(f"{music.name} - {music.artists_str} 下载失败 ({e})")
        finally:
            DOWNLOAD_QUEUE.task_done()


def start_download_threads(num_threads: int):
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=download_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    return threads


CONFIG_PATH = Path("config.json")
CONFIG = load_config()
DOWNLOAD_QUEUE = queue.Queue()
STOP_FLAG = False
threads = start_download_threads(CONFIG.num_threads)


def save_shorten(s: str, width: int, placeholder: str = "..."):
    if width <= len(placeholder):
        # 如果宽度太窄，至少保留第一个字符 + 省略号
        return s[: max(1, width - len(placeholder))] + placeholder

    shortened = textwrap.shorten(s, width=width, placeholder=placeholder)

    # 如果只剩 placeholder，则手动截断
    if shortened == placeholder:
        return s[: width - len(placeholder)] + placeholder

    return shortened


def print_platform(platforms: list[MusicPlatform]):
    table = PrettyTable()
    table.set_style(PLAIN_COLUMNS)
    table.align = "l"
    table.padding_width = 0
    table.title = "平台列表"
    table.field_names = ["选项", "平台"]
    for i, platform in enumerate(platforms):
        table.add_row([f"[{i+1}]", platform.name])
    table.add_row(["[0]", "退出程序"])
    print(table)


def print_query_result(result: MusicQueryResult, title: str, print_download_all: bool):
    table = PrettyTable()
    table.set_style(PLAIN_COLUMNS)
    table.align = "l"
    table.padding_width = 0
    table.title = title
    table.field_names = ["选项", "歌曲", "歌手", "专辑"]
    for i, music in enumerate(result):
        table.add_row(
            [
                f"[{i+1}]",
                save_shorten(music.name, CONFIG.shorten),
                save_shorten(music.artists_str, CONFIG.shorten),
                save_shorten(music.album, CONFIG.shorten),
            ]
        )
    table.add_row(["[0]", "返回搜索", "", ""])
    if print_download_all:
        table.add_row([f"[{len(result)+1}]", "下载全部", "", ""])
    else:
        table.add_row([f"[{len(result)+1}]", "上一页", "", ""])
        table.add_row([f"[{len(result)+2}]", "下一页", "", ""])
    print(table)


def print_music_item(platform: MusicPlatform, music: Music):
    table = PrettyTable()
    table.set_style(PLAIN_COLUMNS)
    table.align = "l"
    table.padding_width = 0
    table.title = f"{platform.name} > 音乐 > {music.name}"
    table.field_names = ["选项", "操作"]
    table.add_row([f"[{1}]", "下载"])
    for i, artist in enumerate(music.artists):
        table.add_row([f"[{i+2}]", f"搜索歌手: {artist}"])
    if music.album_id:
        table.add_row([f"[{2+len(music.artists)}]", f"搜索专辑: {music.album}"])
    table.add_row([f"[{0}]", "返回搜索结果"])
    print(table)
