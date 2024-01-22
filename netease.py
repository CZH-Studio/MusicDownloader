from utils import *
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class Netease(Music):
    def __init__(self):
        # 初始化
        class_name = '网易云'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
        cookies = {
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
        super().__init__(class_name, headers, cookies)

    def query(self, keyword: str, page: int) -> Union[List[Tuple[StrInt, str, str]], List[Tuple[StrInt, str, str, StrInt, str]], bool]:
        search_data = {
            "s": keyword,
            "offset": (page - 1) * PAGE_SIZE,
            "limit": PAGE_SIZE,
            "type": 1
        }
        query_url = 'https://music.163.com/api/search/pc'
        try:
            query = requests.post(query_url, params=search_data, headers=self.headers, cookies=self.cookies).text
            query = json.loads(query)["result"]["songs"]
        except requests.exceptions.ConnectionError:
            return False
        except KeyError:
            return True
        if type(query) is not list:
            return True
        query = [(q["id"], q["name"], q["artists"][0]["name"], q["album"]["id"], q["album"]["name"]) for q in query]
        return query

    def get_music_url(self, music_id: StrInt) -> str:
        target_url = 'https://interface3.music.163.com/eapi/song/enhance/player/url'
        d = {"ids": f'[{music_id}]', 'br': 999000}
        data = self.eapi(d)
        music = requests.post(target_url, data=data).text
        music = json.loads(music)
        music_url = music["data"][0]["url"]
        return music_url

    def get_album_info(self, album_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str]]]:
        album_url = 'https://music.163.com/api/album/' + str(album_id)
        album_response = requests.get(album_url, headers=self.headers, cookies=self.cookies).text
        album_info = json.loads(album_response)
        album_name: str = album_info['album']['name']
        artist_name: str = album_info['album']['artist']['name']
        album_info = album_info['album']['songs']
        album_info = [(info['id'], info['name']) for info in album_info]
        return album_name, artist_name, album_info

    def eapi(self, d: dict) -> dict:
        message_content = json.dumps(d)
        message = f'nobody/api/song/enhance/player/urluse{message_content}md5forencrypt'
        message_md5 = hashlib.md5(message.encode('utf-8')).hexdigest()
        message_send = f"/api/song/enhance/player/url-36cd479b6b5-{message_content}-36cd479b6b5-{message_md5}"
        return {
            "params": self.aes_encrypt(message_send, 'e82ckenh8dichen8', 'MODE_ECB')
        }

    @staticmethod
    def aes_encrypt(text, sec_key, algo):
        # iv = b'0102030405060708'  # 初始化向量（IV），需要根据实际需求设置
        cipher = AES.new(sec_key.encode('utf-8'), getattr(AES, algo))
        encrypted_data = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return encrypted_data.hex().upper()


def main():
    netease = Netease()
    netease.run()


if __name__ == '__main__':
    main()
