from utils import *


class Kugou(Music):
    def __init__(self):
        class_name = "酷狗"
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
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5"
        }
        cookies = {}
        self.max_sub_page = 20 // PAGE_SIZE
        if not self.max_sub_page:
            self.max_sub_page = 1
        super().__init__(class_name, headers, cookies)

    def query(self, keyword: str, page: int) -> Union[List[Tuple[StrInt, str, str]], List[Tuple[StrInt, str, str, StrInt, str]], bool]:
        search_data = {
            "keyword": keyword,
            "page": (page + 1) // self.max_sub_page
        }
        query_url = "https://songsearch.kugou.com/song_search_v2"
        try:
            query = requests.get(query_url, params=search_data, headers=self.headers).text
            query = json.loads(query)["data"]["lists"]
        except requests.exceptions.ConnectionError:
            return False
        except KeyError:
            return True
        if type(query) is not list:
            return True
        slice_value = (page - 1) % self.max_sub_page
        query_length = len(query)
        if slice_value * PAGE_SIZE > query_length:
            return True
        slice_value_end = min((slice_value + 1) * PAGE_SIZE, query_length)
        query = query[slice_value * PAGE_SIZE: slice_value_end]
        query = [(q["FileHash"] + '&' + q["AlbumID"], q["SongName"], q["SingerName"], q["AlbumID"], q["AlbumName"]) for q in query]
        return query

    def get_music_url(self, music_id: StrInt) -> str:
        # 酷狗音乐比较奇怪，获取音乐url时需要用musicID和albumID，需要先拆分
        music_id = music_id.split("&")
        album_id = music_id[1]
        music_id = music_id[0]
        timestamp = int(time.time() * 1000)
        info_url = (f"https://wwwapi.kugou.com/yy/index.php?r=play/getdata"
                    f"&callback=jQuery"
                    f"&mid=1"
                    f"&hash={music_id}"
                    f"&platid=4"
                    f"&album_id={album_id}"
                    f"&_={timestamp}")
        music_response = requests.get(info_url, headers=self.headers).text
        music_response = json.loads(music_response[7:-2])
        music_url = music_response['data']['play_url']
        return music_url

    def get_album_info(self, album_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str]]]:
        album_url = f"http://mobilecdnbj.kugou.com/api/v3/album/info?albumid={album_id}"
        album_response = requests.get(album_url, headers=self.headers).text
        album_data = json.loads(album_response)
        album_name = album_data["data"]["albumname"]
        album_artist_name = album_data["data"]["singername"]

        album_url = f"http://mobilecdnbj.kugou.com/api/v3/album/song?albumid={album_id}&page=1&pagesize=-1"
        album_response = requests.get(album_url, headers=self.headers).text
        album_data = json.loads(album_response)["data"]["info"]
        album_data = [d["hash"] for d in album_data]
        album_info = []
        for hash_value in album_data:
            music_url = f"https://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash_value}"
            music_response = requests.get(music_url, headers=self.headers).text
            music_response = json.loads(music_response)
            album_info.append((music_response["hash"] + '&' + str(album_id), music_response["songName"]))
        return album_name, album_artist_name, album_info


def main():
    kugou = Kugou()
    kugou.run()


if __name__ == '__main__':
    main()
