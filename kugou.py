import requests
import json
import time
from utils import *


SEARCH_URL = "https://songsearch.kugou.com/song_search_v2"
MAX_SUB_PAGE = 20 // PAGE_SIZE  # 酷狗音乐每页限定20条，需要设置子页页数
if not MAX_SUB_PAGE:
    MAX_SUB_PAGE = 1
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Origin": "chrome-extension://olaohimdpfifjlhlinbpcomealcebinf",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "none",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5"
}


def get_music_url(music_id, album_id) -> str:
    timestamp = int(time.time() * 1000)
    info_url = (f"https://wwwapi.kugou.com/yy/index.php?r=play/getdata"
                f"&callback=jQuery"
                f"&mid=1"
                f"&hash={music_id}"
                f"&platid=4"
                f"&album_id={album_id}"
                f"&_={timestamp}")
    music_response = requests.get(info_url, headers=HEADERS).text
    music_response = json.loads(music_response[7:-2])
    music_url = music_response['data']['play_url']
    return music_url


def download_music(music_id: str, album_id: int, music_name: str):
    if not os.path.exists('music'):
        os.mkdir('music')
    if os.path.exists('music/' + music_name + '.mp3'):
        print(f"\033[1;31m[Error] {music_name}.mp3 已存在，下载终止。\033[m")
        return
    music_url = get_music_url(music_id, album_id)
    if not music_url:
        print(f"\033[1;31m[Error] 因为版权原因无法获取 {music_name} 的下载链接，下载终止。\033[m")
        return
    music_response = requests.get(music_url)
    with open(f"music/{music_name}.mp3", 'wb') as music_file:
        music_file.write(music_response.content)
    print(f"\033[1;32m[Success] {music_name}.mp3 保存成功。\033[m")


def download_album(album_id):
    album_url = f"http://mobilecdnbj.kugou.com/api/v3/album/info?albumid={album_id}"
    album_response = requests.get(album_url, headers=HEADERS).text
    album_data = json.loads(album_response)
    album_name = album_data["data"]["albumname"]
    album_artist_name = album_data["data"]["singername"]

    album_url = f"http://mobilecdnbj.kugou.com/api/v3/album/song?albumid={album_id}&page=1&pagesize=-1"
    album_response = requests.get(album_url, headers=HEADERS).text
    album_data = json.loads(album_response)["data"]["info"]
    album_data = [d["hash"] for d in album_data]
    music_cnt = len(album_data)
    album_info = []
    for hash_value in album_data:
        music_url = f"https://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash_value}"
        music_response = requests.get(music_url, headers=HEADERS).text
        music_response = json.loads(music_response)
        album_info.append({"name": music_response["songName"], "id": music_response["hash"]})
    print_album(album_info, "name", album_name, album_artist_name)
    choice_album = input_int(0, music_cnt + 1)
    if choice_album == 0:
        clear_screen()
    elif 1 <= choice_album <= music_cnt:
        music_name = album_info[choice_album - 1]["name"]
        music_id = album_info[choice_album - 1]["id"]
        download = input_int(0, 1, f"是否下载 {music_name} ？(1/0)：")
        if download:
            download_music(music_id, album_id, music_name)
        else:
            clear_screen()


def main():
    while True:
        name = input("[酷狗音乐]请输入搜索的歌曲名，输入0退出：")
        page = 1
        if name == '0':
            break
        while True:
            flag_exit = False
            search_data = {
                "keyword": name,
                "page": (page + 1) // MAX_SUB_PAGE
            }
            query = requests.get(SEARCH_URL, params=search_data, headers=HEADERS).text
            try:
                query = json.loads(query)["data"]["lists"]
            except KeyError:
                print("\033[1;31m[Error] 翻页到头啦！\033[m")
                if page == 1:
                    break
                else:
                    page -= 1
                continue
            if type(query) != list:
                raise TypeError
            slice_value = (page - 1) % MAX_SUB_PAGE
            query_length = len(query)
            if slice_value * PAGE_SIZE > query_length:
                print("\033[1;31m[Error] 翻页到头啦！\033[m")
                if page == 1:
                    break
                else:
                    page -= 1
                continue
            slice_value_end = min((slice_value + 1) * PAGE_SIZE, query_length)
            query = query[slice_value * PAGE_SIZE: slice_value_end]
            query = [[q["FileHash"], q["AlbumID"], q["SongName"], q["SingerName"], q["AlbumName"]] for q in query]
            page_size = len(query)
            while True:
                print_query(query, page)
                choice = input_int(0, page_size * 2 + 2)
                if choice == 0:
                    # 返回搜索
                    flag_exit = True
                    clear_screen()
                    break
                elif 1 <= choice <= page_size:
                    # 选择了一个歌曲
                    download = input_int(0, 1, f"是否下载 {query[choice - 1][2]}-{query[choice - 1][3]}-{query[choice - 1][4]} ？(1/0)：")
                    if download:
                        download_music(query[choice - 1][0], query[choice - 1][1], query[choice - 1][2])
                    else:
                        clear_screen()
                elif page_size + 1 <= choice <= 2 * page_size:
                    # 选择了一个专辑
                    clear_screen()
                    download_album(query[choice - page_size - 1][1])
                elif choice == 2 * page_size + 1:
                    # 上一页
                    if page != 1:
                        page -= 1
                    clear_screen()
                    break
                else:
                    # 下一页
                    page += 1
                    clear_screen()
                    break
            if flag_exit:
                break


if __name__ == '__main__':
    main()
