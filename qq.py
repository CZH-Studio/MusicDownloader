from utils import *
from music import Music


class QQ(Music):
    def __init__(self):
        # 初始化
        class_name = "QQ"
        headers = {
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
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
            "Referer": "https://y.qq.com/"
        }
        cookies = {
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
        super().__init__(class_name, headers, cookies)

    def query(self, keyword: str, page: int) -> Union[List[Tuple[StrInt, str, str]], List[Tuple[StrInt, str, str, StrInt, str]], bool]:
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
                    "query": keyword,
                    "search_type": 0
                }
            }
        }
        search_data = json.dumps(search_data, ensure_ascii=False).encode("utf-8")
        query_url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        try:
            query = requests.post(query_url, data=search_data, headers=self.headers, cookies=self.cookies).text
            query = json.loads(query)["req"]["data"]["body"]["song"]["list"]
        except requests.exceptions.ConnectionError:
            return False
        except KeyError:
            return True
        if type(query) is not list:
            return True
        query = [(q["mid"], q["name"], q["singer"][0]["name"], q["album"]["mid"], q["album"]["name"]) for q in query]
        return query

    def get_music_url(self, music_id: StrInt) -> str:
        target_url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
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
        music = requests.get(target_url, params=params, headers=self.headers, cookies=self.cookies).text
        music = json.loads(music)
        music_url = music["req_0"]["data"]["midurlinfo"][0]["purl"]
        if music_url:
            return 'http://ws.stream.qqmusic.qq.com/' + music_url
        else:
            return ''

    def get_album_info(self, album_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str]]]:
        album_url = "https://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg" + \
                    "?platform=h5page&albummid=" + str(album_id) + \
                    "&g_tk=938407465&uin=0&format=json&inCharset=utf-8&outCharset=utf-8" + \
                    "&notice=0&platform=h5&needNewCode=1&_=1459961045571"
        album_response = requests.get(album_url, headers=self.headers, cookies=self.cookies).text
        album_info = json.loads(album_response)
        album_name: str = album_info["data"]["name"]
        artist_name: str = album_info["data"]["singername"]
        album_info = album_info["data"]["list"]
        album_info = [(item["songmid"], item["songname"]) for item in album_info]
        return album_name, artist_name, album_info

    @staticmethod
    def is_song_list_url(keyword: str) -> StrInt:
        if keyword.startswith("https://i.y.qq.com/n2/m/share/details/taoge.html"):
            return get_parameter_value(keyword, "id")
        else:
            return ''

    def get_song_list_info(self, song_list_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str, str, StrInt, str]]]:
        song_list_url = (f"https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?"
                         f"type=1&json=1&utf8=1&onlysong=0&disstid={song_list_id}"
                         f"&format=json&g_tk=5381&loginUin=0&hostUin=0&inCharset=utf8"
                         f"&outCharset=utf-8%C2%ACice=0&platform=yqq&needNewCode=0")
        song_list_response = requests.get(song_list_url, headers=self.headers, cookies=self.cookies).text
        song_list_info = json.loads(song_list_response)
        song_list_name: str = song_list_info["cdlist"][0]["dissname"]
        song_list_creator: str = song_list_info["cdlist"][0]["nickname"]
        song_list_info = song_list_info["cdlist"][0]["songlist"]
        song_list_info = [(q["songmid"], q["songname"], q["singer"][0]["name"], q["albummid"], q["albumname"]) for q in song_list_info]
        return song_list_name, song_list_creator, song_list_info


def main():
    qq = QQ()
    qq.run()


if __name__ == '__main__':
    main()
