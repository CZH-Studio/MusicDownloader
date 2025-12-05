import random
import hashlib
import base64
import json
from binascii import hexlify

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from utils import CONFIG, MusicQueryResult, Music
from music_platform import MusicPlatform, MusicQueryResult, ResponseCode, Artist


class Netease(MusicPlatform):
    def __init__(self):
        # 初始化
        name = "网易云音乐"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "https://music.163.com/",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Origin": "https://music.163.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
        }
        cookies = {"NMTID": "00OhBuQwHZaM1mn40rEhgzzDRjmfIMAAAGGSxoCUA"}

        super().__init__(name, headers, cookies)

    def query_keyword(self, keyword: str, page: int) -> MusicQueryResult:
        url = "https://music.163.com/api/search/pc"
        data = {
            "s": keyword,
            "offset": (page - 1) * CONFIG.page_size,
            "limit": CONFIG.page_size,
            "type": 1,
        }
        try:
            response = requests.post(
                url,
                params=data,
                headers=self.headers,
                cookies=self.cookies,
            ).json()["result"]["songs"]
            result = [
                Music(
                    item["name"],
                    str(item["id"]),
                    [
                        Artist(artist["name"], str(artist["id"]))
                        for artist in item["artists"]
                    ],
                    item["album"]["name"],
                    str(item["album"]["id"]),
                )
                for item in response
            ]
            return MusicQueryResult(ResponseCode.Success, result)
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
        except KeyError:
            return MusicQueryResult(ResponseCode.FormatError, [])

    def get_music_url(self, music_id: str) -> str:
        url = "https://interface3.music.163.com/eapi/song/enhance/player/url"
        d = {"ids": f"[{music_id}]", "br": 999000}
        data = self._eapi(d)
        response = requests.post(url, data=data).json()
        music_url = response["data"][0]["url"]
        return music_url

    def query_album(self, album_id: str) -> MusicQueryResult:
        album_url = "https://music.163.com/api/album/" + str(album_id)
        try:
            response = requests.get(
                album_url, headers=self.headers, cookies=self.cookies
            ).json()
            album_name: str = response["album"]["name"]
            artist_name: str = response["album"]["artist"]["name"]
            musics = response["album"]["songs"]
            result = [
                Music(
                    item["name"],
                    str(item["id"]),
                    [
                        Artist(artist["name"], str(artist["id"]))
                        for artist in item["artists"]
                    ],
                    item["album"]["name"],
                    str(item["album"]["id"]),
                )
                for item in musics
            ]
            return MusicQueryResult(
                ResponseCode.Success,
                result,
                {"album_name": album_name, "artist_name": artist_name},
            )
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
        except KeyError:
            return MusicQueryResult(ResponseCode.FormatError, [])

    def query_artist(self, artist_id: str) -> MusicQueryResult:
        url = "https://music.163.com/api/artist/" + artist_id
        try:
            response = requests.get(
                url, headers=self.headers, cookies=self.cookies
            ).json()
            musics = response["hotSongs"]
            result = [
                Music(
                    item["name"],
                    str(item["id"]),
                    [
                        Artist(artist["name"], str(artist["id"]))
                        for artist in item["artists"]
                    ],
                    item["album"]["name"],
                    str(item["album"]["id"]),
                )
                for item in musics
            ]
            return MusicQueryResult(ResponseCode.Success, result)
        except requests.exceptions.ConnectionError:
            return MusicQueryResult(ResponseCode.ConnectionError, [])
        except KeyError:
            return MusicQueryResult(ResponseCode.FormatError, [])

    def _eapi(self, d: dict) -> dict:
        message_content = json.dumps(d)
        message = f"nobody/api/song/enhance/player/urluse{message_content}md5forencrypt"
        message_md5 = hashlib.md5(message.encode("utf-8")).hexdigest()
        message_send = f"/api/song/enhance/player/url-36cd479b6b5-{message_content}-36cd479b6b5-{message_md5}"
        return {
            "params": self._aes_encrypt_ECB(message_send, "e82ckenh8dichen8")
            .hex()
            .upper()
        }

    def _weapi(self, d: dict) -> dict:
        modulus = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b72"
            "5152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbd"
            "a92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe48"
            "75d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        )
        nonce = "0CoJUm6Qyw8W8jud"
        pub_key = "010001"
        text = json.dumps(d, ensure_ascii=False)
        sec_key = self._create_secret_key(16)
        enc_text = self._aes_encrypt_CBC(text, nonce)
        enc_text = base64.b64encode(enc_text).decode("utf-8")
        enc_text = self._aes_encrypt_CBC(enc_text, sec_key)
        enc_text = base64.b64encode(enc_text).decode("utf-8")
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
        enc_hex = hex(enc)[2:].rjust(256, "0")
        return enc_hex

    @staticmethod
    def _create_secret_key(size: int) -> str:
        result = ""
        chars = "012345679abcdef"
        for i in range(size):
            result += random.choice(chars)
        return result

    @staticmethod
    def _aes_encrypt_CBC(text, sec_key):
        iv = b"0102030405060708"
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode("utf-8")) + padder.finalize()
        cipher = Cipher(
            algorithms.AES(sec_key.encode("utf-8")),
            modes.CBC(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext
        # iv = b'0102030405060708'  # 初始化向量（IV），需要根据实际需求设置

    @staticmethod
    def _aes_encrypt_ECB(text, sec_key):
        cipher = AES.new(sec_key.encode("utf-8"), getattr(AES, "MODE_ECB"))
        encrypted_data = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
        return encrypted_data
