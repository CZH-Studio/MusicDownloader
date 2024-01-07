import os.path
import requests
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from utils import *

SEARCH_URL = 'https://music.163.com/api/search/pc'
ALBUM_URL = 'https://music.163.com/api/album/'
TARGET_URL = 'https://interface3.music.163.com/eapi/song/enhance/player/url'
EAPI_URL = '/api/song/enhance/player/url'
COOKIES = {
    "NMTID": "00OhBuQwHZaM1mn40rEhgzzDRjmfIMAAAGGSxoCUA",
    "nts_mail_user": "czh666czh666czh666@163.com:-1:1",
    "WEVNSM": "1.0.0",
    "WNMCID": "sqylbk.1677759004659.01.0",
    "WM_TID": "EMsziQvipGNERERBUAOFbcxNX82gALYo",
    "_iuqxldmzr_": "32",
    "ntes_utid": "tid._.QesfzQ4kDplFRwRAAAPFwCC8HVJDKnK6._.0",
    "sDeviceId": "YD-RY3kMdg5lAJFVgEQQFKBbd6W3SR06Cg5",
    "JSESSIONID-WYYY": "QwXMV1kUR9qgE9BNm7nlYqRP%2Fb0j9CCmvjbYhMDwEeHVdX%5CYaKN4XK3fIRe8BWa4V2A7%5CEuVU2NA10kuc%2FjutZ5zVK8drlmVJTNDsJBjWkCR2ZfRCvad5WW%5CHBor1zOtlJrafA8uwaH8tssyCATwTYVn8utzJS9d34tmgkuq3dYJNO7r%3A1695781277942",
    "WM_NI": "gpoOCYVjBkp6wZeXWY6mZI5ZTKtaLBaG17ngTNo8dnLgCD5XOG6K2y9rPiW86yQxQauCKg5oIqv5aOUF%2BDmo3n5aAfmZ9r1KAzz5kFEvh%2F9N5qIjpfv3U8HI7r9a3qHkbXA%3D",
    "WM_NIKE": "9ca17ae2e6ffcda170e2e6eeacef7d81bcae82ce73f2968ba2d85a839a9f86c13994bca8bbb252b1ad8984aa2af0fea7c3b92aa5b0a1b0c25396b68e8cf33eb586abb9d653f6b396aab8529895bc82cf4aa399ffd8ed6d9892a1d9e76690b98da5b8548d99faacb173fbaea08ad634f6a79f99d46bb79d8588b8658bafbad6e445979ae5a5f065f1b2fb82c46eaf86f793b44183a6b6d6ea4e87aaa8d0bc46f7af878bf36eb6ed9bd9cb43f5aef782b27b8cb5aeb9c437e2a3",
    "_ntes_nuid":
        "0121ced343afaf25636c4490cc0d0d64",
    "_ntes_nnid":
        "0121ced343afaf25636c4490cc0d0d64,1701762855906",
    "NTES_P_UTID":
        "9YSGoOfkbTZ43iShO8WDt6hH17pFRXgK|1703404139",
    "P_INFO":
        "czh666czh666czh666@163.com|1703404139|0|mail163|00&99|null&null&null#hlj&231100#10#0#0|&0||czh666czh666czh666@163.com"
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
EAPI_KEY = 'e82ckenh8dichen8'


def aes_encrypt(text, sec_key, algo):
    # iv = b'0102030405060708'  # 初始化向量（IV），需要根据实际需求设置
    cipher = AES.new(sec_key.encode('utf-8'), getattr(AES, algo))
    encrypted_data = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    return encrypted_data.hex().upper()


def eapi(d: dict) -> dict:
    message_content = json.dumps(d)
    message = f'nobody{EAPI_URL}use{message_content}md5forencrypt'
    message_md5 = hashlib.md5(message.encode('utf-8')).hexdigest()
    message_send = f"{EAPI_URL}-36cd479b6b5-{message_content}-36cd479b6b5-{message_md5}"
    return {
        "params": aes_encrypt(message_send, EAPI_KEY, 'MODE_ECB')
    }


def get_music_url(music_id: int) -> str:
    d = {"ids": f'[{music_id}]', 'br': 999000}
    data = eapi(d)
    music = requests.post(TARGET_URL, data=data).text
    music = json.loads(music)
    music_url = music["data"][0]["url"]
    return music_url


def download_music(music_id: int, music_name: str):
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
    album_url = ALBUM_URL + str(album_id)
    album_response = requests.get(album_url, headers=HEADERS, cookies=COOKIES).text
    album_info = json.loads(album_response)
    album_name = album_info['album']['name']
    album_artist_name = album_info['album']['artist']['name']
    album_info = album_info['album']['songs']
    print_album(album_info, 'name', album_name, album_artist_name)
    music_cnt = len(album_info)
    choice_album = input_int(0, music_cnt + 1)
    if choice_album == 0:
        clear_screen()
    elif 1 <= choice_album <= music_cnt:
        music_name = album_info[choice_album - 1]['name']
        music_id = album_info[choice_album - 1]['id']
        download = input_int(0, 1, f"是否下载 {music_name} ？(1/0)：")
        if download:
            download_music(music_id, music_name)
        else:
            clear_screen()
    else:
        download = input_int(0, 1, f"是否下载专辑中的全部歌曲？(1/0)：")
        if download:
            for i in range(music_cnt):
                music_name = album_info[i]['name']
                music_id = album_info[i]['id']
                download_music(music_id, music_name)
        else:
            clear_screen()


def main():
    while True:
        name = input("[网易云音乐]请输入搜索的歌曲名，输入0退出：")
        page = 0
        if name == '0':
            break
        while True:
            flag_exit = False
            search_data = {
                "s": name,
                "offset": page * PAGE_SIZE,
                "limit": PAGE_SIZE,
                "type": 1
            }
            query = requests.post(SEARCH_URL, params=search_data, headers=HEADERS, cookies=COOKIES).text
            try:
                query = json.loads(query)["result"]["songs"]
            except KeyError:
                print("\033[1;31m[Error] 翻页到头啦！\033[m")
                if page == 0:
                    break
                else:
                    page -= 1
                continue
            if type(query) != list:
                raise TypeError
            query = [[q["id"], q["album"]["id"], q["name"], q["artists"][0]["name"], q["album"]["name"]] for q in query]
            # 歌曲名称 歌曲id 艺术家 专辑名称 专辑id
            page_size = len(query)
            while True:
                print_query(query, page + 1)
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
                    download_album(query[choice - page_size - 1][1])
                elif choice == 2 * page_size + 1:
                    # 上一页
                    if page != 0:
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
