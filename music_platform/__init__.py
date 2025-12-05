from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


@dataclass
class Artist:
    name: str
    artist_id: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


@dataclass
class Music:
    name: str
    music_id: str
    artists: list[Artist]
    album: str
    album_id: str

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Music) and self.music_id == value.music_id

    @property
    def artists_str(self) -> str:
        return ", ".join(map(str, self.artists))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "music_id": self.music_id,
            "artists": self.artists_str,
            "album": self.album,
            "album_id": self.album_id,
        }


class ResponseCode(Enum):
    Success = 0
    ConnectionError = 1
    FormatError = 2
    MaxPage = 3


@dataclass
class MusicQueryResult:
    code: ResponseCode
    musics: list[Music]
    meta: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.musics)

    def __getitem__(self, index: int) -> Music:
        return self.musics[index]

    def __contains__(self, item: Music) -> bool:
        return item in self.musics

    def __iter__(self):
        return iter(self.musics)


class MusicPlatform(ABC):
    def __init__(
        self,
        name: str,
        headers: dict,
        cookies: dict,
        ext: str = "mp3",
    ):
        self.name = name  # 模块名称
        self.headers = headers  # 请求头
        self.cookies = cookies  # cookie
        self.ext = ext  # 下载的文件扩展名

    @abstractmethod
    def query_keyword(self, keyword: str, page: int) -> MusicQueryResult:
        pass

    @abstractmethod
    def query_album(self, album_id: str) -> MusicQueryResult:
        pass

    @abstractmethod
    def query_artist(self, artist_id: str) -> MusicQueryResult:
        pass

    @abstractmethod
    def get_music_url(self, music_id: str) -> str:
        pass
