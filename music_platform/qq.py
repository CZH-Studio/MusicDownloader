import json

import requests

from utils import CONFIG
from music_platform import MusicPlatform, MusicQueryResult, Music, ResponseCode, Artist


class QQ(MusicPlatform):
    def __init__(self):
        # 初始化
        platform_name = "QQ音乐"
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
            "Referer": "https://y.qq.com/",
        }
        cookies = {}
        super().__init__(platform_name, headers, cookies)

    def query_keyword(self, keyword: str, page: int) -> MusicQueryResult:
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "comm": {"ct": "19", "cv": "1859", "uin": "0"},
            "req": {
                "method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {
                    "grp": 1,
                    "num_per_page": CONFIG.page_size,
                    "page_num": page,
                    "query": keyword,
                    "search_type": 0,
                },
            },
        }
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        try:
            response = requests.post(
                url, data=data, headers=self.headers, cookies=self.cookies
            ).json()["req"]["data"]["body"]["song"]["list"]
            query_result = [
                Music(
                    item["name"],
                    item["mid"],
                    [
                        Artist(artist["name"], artist["mid"])
                        for artist in item["singer"]
                    ],
                    item["album"]["name"],
                    item["album"]["mid"],
                )
                for item in response
            ]
            return MusicQueryResult(ResponseCode.Success, query_result)
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
        except KeyError:
            return MusicQueryResult(ResponseCode.FormatError, [])

    def get_music_url(self, music_id: str) -> str:
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "req_0": {
                "module": "vkey.GetVkeyServer",
                "method": "CgiGetVkey",
                "param": {
                    "filename": [f"M500{music_id}{music_id}.mp3"],
                    "guid": "10000",
                    "songmid": [music_id],
                    "songtype": [0],
                    "uin": "0",
                    "loginflag": 1,
                    "platform": "20",
                },
            },
            "loginUin": "0",
            "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0},
        }
        params = {
            "format": "json",
            "data": json.dumps(data, ensure_ascii=False).encode("utf-8"),
        }
        response = requests.get(
            url, params=params, headers=self.headers, cookies=self.cookies
        ).json()
        music_url = response["req_0"]["data"]["midurlinfo"][0]["purl"]
        if music_url:
            return "http://ws.stream.qqmusic.qq.com/" + music_url
        else:
            return ""

    def query_album(self, album_id: str) -> MusicQueryResult:
        url = (
            "https://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg"
            + "?platform=h5page&albummid="
            + str(album_id)
            + "&g_tk=938407465&uin=0&format=json&inCharset=utf-8&outCharset=utf-8"
            + "&notice=0&platform=h5&needNewCode=1"
        )
        try:
            response = requests.get(
                url, headers=self.headers, cookies=self.cookies
            ).json()
            album_name = response["data"]["name"]
            artist_name = response["data"]["singername"]
            musics = [
                Music(
                    item["songname"],
                    item["songmid"],
                    [
                        Artist(artist["name"], artist["mid"])
                        for artist in item["singer"]
                    ],
                    item["albumname"],
                    item["albummid"],
                )
                for item in response["data"]["list"]
            ]
            return MusicQueryResult(
                ResponseCode.Success,
                musics,
                {"album_name": album_name, "artist_name": artist_name},
            )
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
        except KeyError:
            return MusicQueryResult(ResponseCode.FormatError, [])

    def query_artist(self, artist_id: str) -> MusicQueryResult:
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "comm": {"ct": 24, "cv": 0},
            "singer": {
                "method": "get_singer_detail_info",
                "param": {
                    "sort": 5,
                    "singermid": artist_id,
                    "sin": 0,
                    "num": 50,
                },
                "module": "music.web_singer_info_svr",
            },
        }
        params = {
            "format": "json",
            "loginUin": 0,
            "hostUin": "0inCharset=utf8",
            "outCharset": "utf-8",
            "platform": "yqq.json",
            "needNewCode": 0,
            "data": json.dumps(data, ensure_ascii=False).encode("utf-8"),
        }
        try:
            response = requests.get(
                url, params=params, headers=self.headers, cookies=self.cookies
            ).json()
            songlist = response["singer"]["data"]["songlist"]
            musics = [
                Music(
                    item["name"],
                    item["mid"],
                    [
                        Artist(artist["name"], artist["mid"])
                        for artist in item["singer"]
                    ],
                    item["album"]["name"],
                    item["album"]["mid"],
                )
                for item in songlist
            ]
            artist_name = response["singer"]["data"]["singer_info"]["name"]
            return MusicQueryResult(
                ResponseCode.Success, musics, {"artist_name": artist_name}
            )
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
