from dataclasses import dataclass, asdict
from pathlib import Path
import os
import json
import queue
import threading
import textwrap
import re
import unicodedata

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


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _is_windows_reserved(name: str) -> bool:
    # 比较时大小写不敏感，且如果名字等于保留名或以保留名加点开头也视为保留
    upp = name.upper()
    for r in WINDOWS_RESERVED_NAMES:
        if upp == r or upp.startswith(r + "."):
            return True
    return False


def sanitize_filename(
    name: str,
    replacement: str = "_",
    platform: str = "auto",
    max_length: int | None = None,
) -> str:
    """
    将 name 中不合法的文件名字符替换为 replacement。
    platform: "auto" (根据 os.name 推断), "windows", "posix", "cross"（更严格）
    max_length: 可选，截断到指定长度（保留扩展名的情况下可自行改造）
    """
    if name is None:
        return ""
    # 规范化 Unicode（可选，避免奇怪的组合字符）
    name = unicodedata.normalize("NFKC", str(name))

    # 选择规则
    import os

    pf = platform.lower()
    if pf == "auto":
        pf = "windows" if os.name == "nt" else "posix"
    if pf not in {"windows", "posix", "cross"}:
        raise ValueError("platform must be 'auto','windows','posix' or 'cross'")

    if pf == "windows":
        # Windows 不允许: <>:"/\\|?* 以及 0-31 控制字符
        forbidden = re.compile(r'[<>:"/\\|?\*\x00-\x1F]')
    elif pf == "posix":
        # POSIX 只禁止 / 和 NUL 字符（\x00）
        forbidden = re.compile(r"[\/\x00]")
    else:  # cross (严格): 合并两者并去掉一些常见危险符
        forbidden = re.compile(r'[<>:"/\\|?\*\x00-\x1F]')

    # 替换
    safe = forbidden.sub(replacement, name)

    # Windows 不能以空格或点结尾 — 去掉尾部空格和点（替换为 replacement）
    if pf == "windows" or pf == "cross":
        # 将尾部的空格或点全部替换（不直接strip以免丢失信息，改为替换为 replacement）
        # 示例: "file. " -> "file_"
        m = re.search(r"[ \.]+$", safe)
        if m:
            safe = re.sub(r"[ \.]+$", replacement, safe)

    # 如果变成空串，返回单下划线（或 replacement）
    if safe == "":
        safe = replacement

    # 避免保留名（Windows）
    if pf == "windows" or pf == "cross":
        if _is_windows_reserved(safe):
            safe = safe + replacement

    # 可选截断
    if max_length is not None and isinstance(max_length, int) and max_length > 0:
        if len(safe) > max_length:
            safe = safe[:max_length]

    return safe


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


def print_episodes(
    platform: MusicPlatform, music: Music, episodes: list[tuple[str, str]]
):
    table = PrettyTable()
    table.set_style(PLAIN_COLUMNS)
    table.align = "l"
    table.padding_width = 0
    table.title = f"{platform.name} > 音乐 > {music.name} > 选集"
    table.field_names = ["选项", "集"]
    for i, (_, episode_name) in enumerate(episodes):
        table.add_row([f"[{i+1}]", episode_name])
    table.add_row([f"[{len(episodes) + 1}]", "下载全部"])
    table.add_row([f"[{0}]", "返回"])
    print(table)
