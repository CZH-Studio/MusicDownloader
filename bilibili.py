import json
import requests
import re
from utils import *


SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type?"
HEADERS_SEARCH = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "none",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5"
}
COOKIES = {
    "buvid3": "2E109C72-251F-3827-FA8E-921FA0D7EC5291319infoc",
    "b_nut": "1676213591",
    "i-wanna-go-back": "-1",
    "_uuid": "2B2D7A6C-8310C-1167-F548-2F1095A6E93F290252infoc",
    "buvid4": "31696B5F-BB23-8F2B-3310-8B3C55FB49D491966-023021222-WcoPnBbwgLUAZ6TJuAUN8Q%3D%3D",
    "CURRENT_FNVAL": "4048",
    "DedeUserID": "520271156",
    "DedeUserID__ckMd5": "66450f2302095cc5",
    "nostalgia_conf": "-1",
    "rpdid": "|(JY))RmR~|u0J'uY~YkuJ~Ru",
    "buvid_fp_plain": "undefined",
    "b_ut": "5",
    "hit-dyn-v2": "1",
    "LIVE_BUVID": "AUTO8716766313471956",
    "hit-new-style-dyn": "1",
    "CURRENT_PID": "418c8490-cadb-11ed-b23b-dd640f2e1c14",
    "FEED_LIVE_VERSION": "V8",
    "header_theme_version": "CLOSE",
    "CURRENT_QUALITY": "80",
    "enable_web_push": "DISABLE",
    "buvid_fp": "52ad4773acad74caefdb23875d5217cd",
    "PVID": "1",
    "home_feed_column": "5",
    "SESSDATA": "8036f42c%2C1719895843%2C19675%2A12CjATThdxG8TyQ2panBpBQcmT0gDKjexwc-zXNGiMnIQ2I9oLVmOiE9YkLao2_aawEhoSVlhGY05PVjVkZWM0T042Z2hZRXBOdElYWXhJa3RpVmZ0M3NvcWw1N0tPcGRVSmRoOVNQZnNHT1JHS05yR1Y1MUFLX3RXeXVJa3NjbEVBQkUxRVN6RFRRIIEC",
    "bili_jct": "4c583b61b86b16d812a7804078828688",
    "sid": "8dt1ioao",
    "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDQ2MjUzNjAsImlhdCI6MTcwNDM2NjEwMCwicGx0IjotMX0.4E-V4K2y452cy6eexwY2x_q3-xgcNF2qtugddiuF8d4",
    "bili_ticket_expires": "1704625300",
    "fingerprint": "847f1839b443252d91ff0df7465fa8d9",
    "browser_resolution": "1912-924",
    "bp_video_offset_520271156": "883089613008142344"
}
HEADERS_DOWNLOAD = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.bilibili.com/"
}


def get_music_url(music_id: str) -> str:
    api_url_1 = f"https://api.bilibili.com/x/web-interface/view?bvid={music_id}"
    api_response_1 = requests.get(api_url_1, headers=HEADERS_SEARCH, cookies=COOKIES).text
    cid = json.loads(api_response_1)['data']['cid']
    api_url_2 = f"https://api.bilibili.com/x/player/playurl?fnval=16&bvid={music_id}&cid={cid}"
    api_response_2 = requests.get(api_url_2, headers=HEADERS_SEARCH, cookies=COOKIES).text
    api_response_2 = json.loads(api_response_2)
    music_url = api_response_2['data']['dash']['audio'][0]['baseUrl']
    return music_url


def download_music(music_id: str, music_name: str):
    if not os.path.exists('music'):
        os.mkdir('music')
    if os.path.exists('music/' + music_name + '.aac'):
        print(f"\033[1;31m[Error] {music_name}.aac 已存在，下载终止。\033[m")
        return
    music_url = get_music_url(music_id)
    if not music_url:
        print(f"\033[1;31m[Error] 因为版权原因无法获取 {music_name} 的下载链接，下载终止。\033[m")
        return
    music_response = requests.get(music_url, headers=HEADERS_DOWNLOAD)
    with open(f"music/{music_name}.aac", 'wb') as music_file:
        music_file.write(music_response.content)
    print(f"\033[1;32m[Success] {music_name}.aac 保存成功。\033[m")


def get_raw_content(s) -> str:
    s = re.sub(r'<em.*?>', '', s)
    s = re.sub(r'</em>', '', s)
    return s


def main():
    while True:
        print("\033[1;33m温馨提示：在哔哩哔哩下载的音乐均为aac格式，音质较差。\033[m")
        name = input("[哔哩哔哩]请输入搜索的歌曲名，输入0退出：")
        page = 1
        if name == '0':
            break
        while True:
            flag_exit = False
            search_url = SEARCH_URL + (f"__refresh__=true"
                                       f"&_extra=&context="
                                       f"&page={page}&page_size={PAGE_SIZE}"
                                       f"&platform=pc&highlight=1"
                                       f"&single_column=0&keyword={name}"
                                       f"&category_id=&search_type=video"
                                       f"&dynamic_offset=0&preload=true"
                                       f"&com2co=true")
            query = requests.get(search_url, headers=HEADERS_SEARCH, cookies=COOKIES).text
            try:
                query = json.loads(query)["data"]["result"]
            except KeyError:
                print("\033[1;31m[Error] 翻页到头啦！\033[m")
                if page == 1:
                    break
                else:
                    page -= 1
                continue
            if type(query) != list:
                raise TypeError
            query = [[q["bvid"], get_raw_content(q["title"]), q["author"]] for q in query]
            page_size = len(query)
            while True:
                print_names(query, page)
                choice = input_int(0, page_size + 2)
                if choice == 0:
                    # 返回搜索
                    flag_exit = True
                    clear_screen()
                    break
                elif 1 <= choice <= page_size:
                    # 选择了一个歌曲
                    download = input_int(0, 1, f"是否下载 {query[choice - 1][1]}-{query[choice - 1][2]} ？(1/0)：")
                    if download:
                        download_music(query[choice - 1][0], query[choice - 1][1])
                    else:
                        clear_screen()
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
