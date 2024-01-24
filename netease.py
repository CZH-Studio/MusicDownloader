import random
from utils import *
import hashlib
from binascii import hexlify
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding

    ENABLE_SONG_LIST = True
except ImportError:
    ENABLE_SONG_LIST = False


class Netease(Music):
    def __init__(self):
        # 初始化
        class_name = '网易云'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
                   "Accept": "application/json, text/plain, */*",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
                   "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                   "Referer": "https://music.163.com/",
                   "Sec-Ch-Ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
                   "Sec-Ch-Ua-Mobile": "?0",
                   "Sec-Ch-Ua-Platform": '"Windows"',
                   "Origin": "https://music.163.com/",
                   "Sec-Fetch-Dest": "empty",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "none"
                   }
        cookies = {
            "NMTID": "00OhBuQwHZaM1mn40rEhgzzDRjmfIMAAAGGSxoCUA",
            "nts_mail_user": "czh666czh666czh666@163.com:-1:1",
            "WEVNSM": "1.0.0",
            "WNMCID": "sqylbk.1677759004659.01.0",
            "WM_TID": "EMsziQvipGNERERBUAOFbcxNX82gALYo",
            "_iuqxldmzr_": "32",
            "ntes_utid": "tid._.QesfzQ4kDplFRwRAAAPFwCC8HVJDKnK6._.0",
            "sDeviceId": "YD-RY3kMdg5lAJFVgEQQFKBbd6W3SR06Cg5",
            "JSESSIONID-WYYY": "uE2DcgJtmu2QGnPu4Pqf9w8KonDF9xJdx%2Fuon%2BCudbe4PNCoPQEA3BnOjS8v3JccBlF%5Cn5%5CqPmZ7smKYRtIfi0NUZjpQpF64TZ7YPnul7VnjHd%2FjKwqgrhxlqTj2%2BRMFpxVZ0H4wBEDg0JimhljxYRD1NtTI6xK2JcP5p%2B1rRvgAuG2p%3A1706006375795",
            "WM_NI": "7MmIeltg8cOkaeCFK%2FDVw4RxPpGWX02ofBhIRKjgIZdjVtQGf4kKGC3NJEdp6t4vnoNUR9qP4lpEHGJE%2Bx7a8pAA1ao3TkYyHbxAxGBf%2BpdDhCDN%2BDEYa3E0cDXhkiw0eE4%3D",
            "WM_NIKE": "9ca17ae2e6ffcda170e2e6ee97ee3c8a998b9ad850aeb88ba6d55f939a8bb1d834f3eba9a3f65cbcf0a990c12af0fea7c3b92af593a3aae868b8b9f884ce61a3bb8da7ca25888ab9d5d17494b089b8db3cf2b1aaa3eb439295a688cc52a8b69a95d44da6eca5acc649f19286a6e77cf6acfc97ed658e8b9edaf45cf8b4c0a6cb4d8a9be599b66bfcb08fa2b46baded9c8cdc738cbeb8a2fb4d82bae591e750ac9d8cafaa508787afd4c83ca19c9889ea63b5f0aba6b737e2a3",
            "__snaker__id": "lrByOVKRqQmttdmO",
            "_ntes_nuid":
                "74205f79cdcf71700ee71e6bfa31f57c",
            "_ntes_nnid":
                "74205f79cdcf71700ee71e6bfa31f57c,1706005791219",
            "NTES_P_UTID":
                "9YSGoOfkbTZ43iShO8WDt6hH17pFRXgK|1705975611",
            "P_INFO":
                "czh666czh666czh666@163.com|1703404139|0|mail163|00&99|null&null&null#hlj&231100#10#0#0|&0||czh666czh666czh666@163.com",
            "MUSIC_U":
                "00C0FA1299BBD04AB2C2C82E4B19FA7C9EB710520B77BCB0EB0479642B9879C0FFB6B058479738015A150A8AEC2A6F207EF7018F4B2371B9FAD917"
                "81E94BDC6E226854D1FD649E5EC4FC5FB7EFF77DBB30CCD642C9737A43D2FEDEA03D1D62A7D3F6678A0CE453921FF82CC60870A28313DC7CB3D727"
                "356C30FCE6B49D9BC1FA176CB5C05584CEEE50C54A982A565254D315DFD378CAF694C9A84B3C79133F37E074841CD8916A37ECA99FD14EDB0B1291"
                "6E174315112F7B35B3CD00EAF1CF2B82A0E1F34B610C7667E51C54DD86BA67CE91EE15416D55E701728D4EC85C4860F1BEDEF2D94C1CABEB5C4B68"
                "8C406B82C9AF6E4C07A269939A214F247A204F94A2BB057A738BBF985D32B86B53C6E37F69CE0815394E16D6E03BFF1BB506B921F0D65F5D19CF57"
                "973972A826C4BD33BF11B3BC35413DB9539E97FD21565AD7698842AD6CDCBFC4FC296EE76A7FCA8C913EF033504F6323C6FA604F09C74DE85D323F"
                "0B035709F9D5208A4DCA90DE357C69",
            "__remember_me": "true",
            "__csrf": "1d18b8d276c9d5b9a3fb0034d5968929",
            "ntes_kaola_ad": "1",
            "gdxidpyhxdE": "v0XWh7PNCItNYMZJMx7ZoXbkg%2BEVEzAEq3zhSGBwzKytS8%2FOwW8LxByAcbwfrkQVePp%5Cda2DpTx%5CehqAhO5XH3zS0ZcX4bkHeBfbsp2%2F5aEgLRA7iB3J%2ByTaTSyC1T%2BaSSKffm%2FHqUbt%5CqtQ1ZN9kyAYvbKiQDor6C80k0TmgEBkZBBn%3A1705990710922"
        }

        super().__init__(class_name, headers, cookies, enable_song_list=ENABLE_SONG_LIST)

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
        data = self._eapi(d)
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

    def get_song_list_info(self, song_list_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str, str, StrInt, str]]]:
        song_list_preview_url = "https://music.163.com/weapi/v3/playlist/detail"
        d = {
            "id": str(song_list_id),
            "offset": 0,
            "total": True,
            "limit": 1000,
            "n": 1000,
            "csrf_token": ""
        }
        d = self._weapi(d)
        song_list_preview_response = requests.post(song_list_preview_url, params=d, headers=self.headers, cookies=self.cookies)
        song_list_preview_response = song_list_preview_response.text
        song_list_preview_info = json.loads(song_list_preview_response)
        song_list_name: str = song_list_preview_info["playlist"]["name"]
        song_list_creator: str = song_list_preview_info["playlist"]["creator"]["nickname"]
        song_list_preview_info = song_list_preview_info["playlist"]["trackIds"]
        track_ids = [q["id"] for q in song_list_preview_info]
        song_list_url = "https://music.163.com/weapi/v3/song/detail"
        d = {
            "c": "[" + ",".join([f'{{"id":{i}}}' for i in track_ids]) + "]",
            "ids": "[" + ",".join(map(str, track_ids)) + "]"
        }
        d = self._weapi(d)
        song_list_response = requests.post(song_list_url, data=d, headers=self.headers, cookies=self.cookies).text
        song_list_info = json.loads(song_list_response)["songs"]
        song_list_info = [(q["id"], q["name"], q["ar"][0]["name"], q["al"]["id"], q["al"]["name"]) for q in song_list_info]
        return song_list_name, song_list_creator, song_list_info

    @staticmethod
    def is_song_list_url(keyword) -> StrInt:
        if keyword.startswith('https://music.163.com/#/playlist'):
            return get_parameter_value(keyword, 'id')
        else:
            return ''

    def _eapi(self, d: dict) -> dict:
        message_content = json.dumps(d)
        message = f'nobody/api/song/enhance/player/urluse{message_content}md5forencrypt'
        message_md5 = hashlib.md5(message.encode('utf-8')).hexdigest()
        message_send = f"/api/song/enhance/player/url-36cd479b6b5-{message_content}-36cd479b6b5-{message_md5}"
        return {
            "params": self._aes_encrypt_ECB(message_send, 'e82ckenh8dichen8').hex().upper()
        }

    def _weapi(self, d: dict) -> dict:
        modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b72'
                   '5152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbd'
                   'a92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe48'
                   '75d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7')
        nonce = '0CoJUm6Qyw8W8jud'
        pub_key = '010001'
        text = json.dumps(d, ensure_ascii=False)
        sec_key = self._create_secret_key(16)
        enc_text = self._aes_encrypt_CBC(text, nonce)
        enc_text = base64.b64encode(enc_text).decode('utf-8')
        enc_text = self._aes_encrypt_CBC(enc_text, sec_key)
        enc_text = base64.b64encode(enc_text).decode('utf-8')
        enc_sec_key = self._rsa_encrypt(sec_key, pub_key, modulus)
        return {
            "params": enc_text,
            "encSecKey": enc_sec_key,
        }

    @staticmethod
    def _rsa_encrypt(text, pub_key, modulus) -> str:
        # for test: text="10", pub_key="20", modulus="30", correct
        text = text[::-1]
        n = int(modulus, 16)
        e = int(pub_key, 16)
        b = int(hexlify(text.encode()), 16)
        enc = pow(b, e, n)
        enc_hex = hex(enc)[2:].rjust(256, '0')
        return enc_hex

    @staticmethod
    def _create_secret_key(size: int) -> str:
        result = ''
        chars = '012345679abcdef'
        for i in range(size):
            result += random.choice(chars)
        return result

    @staticmethod
    def _aes_encrypt_CBC(text, sec_key):
        iv = b'0102030405060708'
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.AES(sec_key.encode('utf-8')), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext
        # iv = b'0102030405060708'  # 初始化向量（IV），需要根据实际需求设置

    @staticmethod
    def _aes_encrypt_ECB(text, sec_key):
        cipher = AES.new(sec_key.encode('utf-8'), getattr(AES, 'MODE_ECB'))
        encrypted_data = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return encrypted_data


def main():
    netease = Netease()
    netease.run()


if __name__ == '__main__':
    main()
