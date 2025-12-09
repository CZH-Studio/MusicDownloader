from pathlib import Path
import time
from dataclasses import replace

from utils import (
    CONFIG,
    input_int,
    cls,
    DOWNLOAD_QUEUE,
    STOP_FLAG,
    print_platform,
    print_query_result,
    print_music_item,
    print_episodes,
    sanitize_filename,
)
from music_platform import MusicPlatform, Music, Artist

from music_platform.netease import Netease
from music_platform.qq import QQ
from music_platform.bilibili import Bilibili

# from music_platform.kugou import Kugou


def artist_loop(platform: MusicPlatform, artist: Artist):
    while True:
        cls()
        result = platform.query_artist(artist.artist_id)
        print_query_result(result, f"{platform.name} > 歌手 > {artist.name}", True)
        choice = input_int("请选择", 0, len(result) + 1, 0)
        if choice == 0:
            break
        elif choice == len(result) + 1:
            download_all(platform, result.musics)
        else:
            item = result[choice - 1]
            item_loop(platform, item)


def album_loop(platform: MusicPlatform, music: Music):
    while True:
        cls()
        result = platform.query_album(music.album_id)
        print_query_result(result, f"{platform.name} > 专辑 > {music.album}", True)
        choice = input_int("请选择", 0, len(result) + 1, 0)
        if choice == 0:
            break
        elif choice == len(result) + 1:
            download_all(platform, result.musics)
        else:
            item = result[choice - 1]
            item_loop(platform, item)


def episode_loop(
    platform: MusicPlatform, music: Music, episodes: list[tuple[str, str]]
):
    while True:
        cls()
        print_episodes(platform, music, episodes)
        choice = input_int("请选择", 0, len(episodes) + 1, 0)
        if choice == 0:
            break
        elif choice == len(episodes) + 1:
            confirm = input_int("确认下载全部音乐?", 0, 1, 1)
            if confirm == 0:
                break
            try:
                for url, episode_name in episodes:
                    filename = (
                        CONFIG.save_filename.format(**music.to_dict())
                        + f" - {episode_name}"
                    )
                    filename = sanitize_filename(filename)
                    path = Path(CONFIG.save_dir) / (filename + f".{platform.ext}")
                    music_new = replace(music, name=music.name + f" - {episode_name}")
                    DOWNLOAD_QUEUE.put(
                        (music_new, url, platform.headers, platform.cookies, path)
                    )
                DOWNLOAD_QUEUE.join()
                time.sleep(2)
            except KeyError:
                print("无法下载，请检查config.json中的save_filename配置！")
                time.sleep(2)
                break
        else:
            url, episode_name = episodes[choice - 1]
            try:
                filename = (
                    CONFIG.save_filename.format(**music.to_dict())
                    + f" - {episode_name}"
                )
                filename = sanitize_filename(filename)
                path = Path(CONFIG.save_dir) / (filename + f".{platform.ext}")
                music_new = replace(music, name=music.name + f" - {episode_name}")
                DOWNLOAD_QUEUE.put(
                    (music_new, url, platform.headers, platform.cookies, path)
                )
                DOWNLOAD_QUEUE.join()
                time.sleep(2)
            except KeyError:
                print("无法下载，请检查config.json中的save_filename配置！")
                time.sleep(2)
                break


def download_one(platform: MusicPlatform, music: Music):
    cls()
    choice = input_int(f"确认下载 {music.name} - {music.artists_str} ?", 0, 1, 1)
    if choice == 0:
        return
    url = platform.get_music_url(music.music_id)
    if url is None:
        print(f"由于版权原因无法下载 {music.name}")
        time.sleep(2)
        return
    elif isinstance(url, str):
        try:
            filename = CONFIG.save_filename.format(**music.to_dict())
            filename = sanitize_filename(filename)
            path = Path(CONFIG.save_dir) / (filename + f".{platform.ext}")
        except KeyError:
            print("无法下载，请检查config.json中的save_filename配置！")
            time.sleep(2)
            return
        DOWNLOAD_QUEUE.put((music, url, platform.headers, platform.cookies, path))
        DOWNLOAD_QUEUE.join()
        time.sleep(2)
    else:
        episode_loop(platform, music, url)


def download_all(platform: MusicPlatform, musics: list[Music]):
    cls()
    choice = input_int("确认下载全部音乐?", 0, 1, 1)
    if choice == 0:
        return
    for music in musics:
        url = platform.get_music_url(music.music_id)
        if url is None:
            print(f"由于版权原因无法下载 {music.name}")
        path = Path(CONFIG.save_dir) / (
            CONFIG.save_filename.format(**music.to_dict()) + f".{platform.ext}"
        )
        DOWNLOAD_QUEUE.put((music, url, platform.headers, platform.cookies, path))
    DOWNLOAD_QUEUE.join()
    time.sleep(2)


def item_loop(platform: MusicPlatform, music: Music):
    while True:
        cls()
        print_music_item(platform, music)
        if music.album_id == "":
            max_choice = 1 + len(music.artists)
        else:
            max_choice = 2 + len(music.artists)
        choice = input_int("请选择", 0, max_choice, 0)
        if choice == 0:
            break
        elif choice == 1:
            download_one(platform, music)
        elif 1 < choice <= 1 + len(music.artists):
            artist = music.artists[choice - 2]
            artist_loop(platform, artist)
        elif choice == 2 + len(music.artists):
            album_loop(platform, music)
        else:
            continue


def browse_loop(platform: MusicPlatform, keyword: str):
    page = 1
    while True:
        cls()
        result = platform.query_keyword(keyword, page)
        if len(result) == 0:
            if page == 1:
                print(
                    f"{platform.name} > 搜索 > {keyword} (第{page}页)\n无结果，2s后返回搜索"
                )
                time.sleep(2)
                break
            else:
                print(
                    f"{platform.name} > 搜索 > {keyword} (第{page}页)\n无结果，2s后返回上一页"
                )
                time.sleep(2)
                page = page - 1
                continue
        print_query_result(
            result, f"{platform.name} > 搜索 > {keyword} (第{page}页)", False
        )
        choice = input_int("请选择", 0, len(result) + 2, 0)
        if choice == 0:
            break
        elif choice == len(result) + 1:
            page = max(page - 1, 1)
        elif choice == len(result) + 2:
            page = page + 1
        else:
            item = result[choice - 1]
            item_loop(platform, item)


def search_loop(platform: MusicPlatform):
    while True:
        cls()
        keyword = input(f"{platform.name} > 搜索: ")
        if keyword == "0" or not keyword:
            break
        browse_loop(platform, keyword)


def main():
    platforms: list[MusicPlatform] = [Netease(), QQ(), Bilibili()]
    while True:
        cls()
        print_platform(platforms)
        choice = input_int("请选择", 0, len(platforms), 0)
        if choice == 0:
            break
        platform = platforms[choice - 1]
        cls()
        search_loop(platform)
    DOWNLOAD_QUEUE.join()
    STOP_FLAG = True
    time.sleep(1)


if __name__ == "__main__":
    main()
