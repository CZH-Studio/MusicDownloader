import requests
import json
from utils import *

SEARCH_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"
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
COOKIES = {
    "tvfe_boss_uuid": "288c72eb2129c389",
    "pgv_pvid": "6847532210",
    "RK": "nw1UVl09Xw",
    "ptcz": "018202ab5016d44eb1f704bb329f9d400a1dcfd2605ab40c338625279896e0e5",
    "fqm_pvqid": "e8ea2c5d-25a3-4538-b928-c1778e790ba3",
    "ts_uid": "5518125330",
    "pac_uid": "1_1248964171",
    "o_cookie": "1248964171",
    "qq_domain_video_guid_verify": "3fdc5b19c19858e7",
    "iip": "0"
}


def get_music_url(music_id: str) -> str:
    req_0 = {
        "req_0": {
            "module": 'vkey.GetVkeyServer',
            "method": 'CgiGetVkey',
            "param": {
                "filename": [f"M500{music_id}{music_id}.mp3"],
                "guid": "10000",
                "songmid": [music_id],
                "songtype": [0],
                "uin": "0",
                "loginflag": 1,
                "platform": "20"
            }
        },
        "loginUin": "0",
        "comm": {
            "uin": "0",
            "format": "json",
            "ct": 24,
            "cv": 0
        }
    }
    params = {
        "format": "json",
        "data": json.dumps(req_0, ensure_ascii=False).encode('utf-8')
    }
    music_response = requests.get(SEARCH_URL, params=params, cookies=COOKIES, headers=HEADERS).text
    music_response = json.loads(music_response)
    music_url = music_response["req_0"]["data"]["midurlinfo"][0]["purl"]
    return 'http://ws.stream.qqmusic.qq.com/' + music_url


def download_music(music_id: str, music_name: str):
    if not os.path.exists('music'):
        os.mkdir('music')
    if os.path.exists('music/' + music_name + '.mp3'):
        print(f"\033[1;31m[Error] {music_name}.mp3 已存在，下载终止。\033[m")
        return
    music_url = get_music_url(music_id)
    if not music_url:
        print(f"\033[1;31m[Error] 因为版权原因无法获取 {music_name} 的下载链接，下载终止。\033[m")
        return
    music_response = requests.get(music_url)
    with open(f"music/{music_name}.mp3", 'wb') as music_file:
        music_file.write(music_response.content)
    print(f"\033[1;32m[Success] {music_name}.mp3 保存成功。\033[m")


def download_album(album_id):
    album_url = "https://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg" + \
                "?platform=h5page&albummid=" + str(album_id) + \
                "&g_tk=938407465&uin=0&format=json&inCharset=utf-8&outCharset=utf-8" + \
                "&notice=0&platform=h5&needNewCode=1&_=1459961045571"
    album_response = requests.get(album_url, headers=HEADERS, cookies=COOKIES).text
    album_info = json.loads(album_response)
    album_name = album_info["data"]["name"]
    album_artist_name = album_info["data"]["singername"]
    album_info = album_info["data"]["list"]
    print_album(album_info, 'songname', album_name, album_artist_name)
    music_cnt = len(album_info)
    choice_album = input_int(0, music_cnt + 1)
    if choice_album == 0:
        clear_screen()
    elif 1 <= choice_album <= music_cnt:
        music_name = album_info[choice_album - 1]['songname']
        music_id = album_info[choice_album - 1]['songmid']
        download = input_int(0, 1, f"是否下载 {music_name} ？(1/0)：")
        if download:
            download_music(music_id, music_name)
        else:
            clear_screen()
    else:
        download = input_int(0, 1, f"是否下载专辑中的全部歌曲？(1/0)：")
        if download:
            for i in range(music_cnt):
                music_name = album_info[i]['songname']
                music_id = album_info[i]['songmid']
                download_music(music_id, music_name)
        else:
            clear_screen()


def main():
    while True:
        name = input("[QQ音乐]请输入搜索的歌曲名，输入0退出：")
        page = 1
        if name == '0':
            break
        while True:
            flag_exit = False
            search_data = {
                "comm": {
                    "ct": "19",
                    "cv": "1859",
                    "uin": "0"
                },
                "req": {
                    "method": "DoSearchForQQMusicDesktop",
                    "module": "music.search.SearchCgiService",
                    "param": {
                        "grp": 1,
                        "num_per_page": PAGE_SIZE,
                        "page_num": page,
                        "query": name,
                        "search_type": 0
                    }
                }
            }
            search_data = json.dumps(search_data, ensure_ascii=False).encode('utf-8')
            query = requests.post(SEARCH_URL, data=search_data, cookies=COOKIES, headers=HEADERS).text
            try:
                query = json.loads(query)["req"]["data"]["body"]["song"]["list"]
            except KeyError:
                print("\033[1;31m[Error] 翻页到头啦！\033[m")
                if page == 1:
                    break
                else:
                    page -= 1
                continue
            if type(query) is not list:
                raise TypeError
            query = [[q["mid"], q["album"]["mid"], q["name"], q["singer"][0]["name"], q["album"]["name"]] for q in query]
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
                        download_music(query[choice - 1][0], query[choice - 1][2])
                    else:
                        clear_screen()
                elif page_size + 1 <= choice <= 2 * page_size:
                    # 选择了一个专辑
                    clear_screen()
                    download_album(query[choice - 1 - page_size][1])
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
