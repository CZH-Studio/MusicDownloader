from utils import *


class Music:
    def __init__(self, class_name: str, headers: dict, cookies: dict, no_album: bool = False, ext: str = "mp3", enable_song_list: bool = True):
        """
        初始化
        :param class_name: 模块名称
        :param headers: 请求头
        :param cookies: cookie
        :param no_album: 是否不包含专辑信息，默认False
        :param ext: 下载的文件扩展名，默认mp3
        :param enable_song_list: 是否可以用歌单搜索，默认True
        """
        # 传参
        self.class_name = class_name  # 模块名称
        self.headers = headers  # 请求头
        self.cookies = cookies  # cookie
        self.no_album = no_album  # 是否不包含专辑信息
        self.ext = ext  # 下载的文件扩展名
        self.enable_song_list = enable_song_list  # 是否可以用歌单搜索
        # 配置
        self.page_size = PAGE_SIZE
        self.max_process = MAX_PROCESS
        self.music_dir = MUSIC_DIR
        self.save_artist = SAVE_ARTIST
        # 全局
        self.download_queue: mp.Queue[Tuple[StrInt, str, str]] = mp.Queue()
        self.illegal_chars = r'[\\/:"*?<>|]+'

    def run(self):
        while True:
            if self.enable_song_list:
                prompt = f"[{self.class_name}音乐]请输入搜索的歌曲名/粘贴歌单链接，直接回车退出："
            else:
                prompt = f"[{self.class_name}音乐]请输入搜索的歌曲名，直接回车退出："
            query_keyword = my_input(prompt)
            if not query_keyword:
                break
            song_list_id = self.is_song_list_url(query_keyword)
            if song_list_id and self.enable_song_list:
                self._download_song_list(song_list_id)
                continue
            page = 1
            while True:
                flag_exit = False
                query = self.query(query_keyword, page)
                # query的结构
                # 含有专辑信息：[[歌曲序号, 歌曲名称, 艺术家, 专辑序号, 专辑名称], ...]
                # 不含专辑信息：[[歌曲序号, 歌曲名称, 艺术家], ...]
                if isinstance(query, bool):
                    if query:
                        my_print("[Error] 查询结果为空或翻页到末尾！", color="red", highlight=True)
                        if page == 1:
                            break
                        else:
                            page -= 1
                            continue
                    else:
                        my_print("[Error] 服务器拒绝响应！", color="red", highlight=True)
                        break
                page_size = len(query)
                while True:
                    print_query(query, page, self.no_album)
                    choice_max = page_size + 2 if self.no_album else page_size * 2 + 2
                    choice = my_input(f"[input] 请输入序号选择([0]~{choice_max})：", t=int, min_val=0, max_val=choice_max, default=0)
                    if choice == 0:
                        # 返回搜索
                        flag_exit = True
                        clear_screen()
                        break
                    elif 1 <= choice <= page_size:
                        # 选择了一个歌曲
                        download = my_input(f"[Input] 是否下载{query[choice - 1][1]}-{query[choice - 1][2]}？([1]/0)：", t=bool, default=True)
                        if download:
                            clear_screen()
                            self._download_music(query[choice - 1][0], query[choice - 1][1])
                        else:
                            clear_screen()
                    elif page_size + 1 <= choice <= page_size * 2 and not self.no_album:
                        # 选择了一个专辑
                        clear_screen()
                        self._download_album(query[choice - page_size - 1][3])
                    elif choice == choice_max - 1:
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
        clear_screen()

    def query(self, keyword: str, page: int) -> Union[List[Tuple[StrInt, str, str]], List[Tuple[StrInt, str, str, StrInt, str]], bool]:
        """
        查询函数，需要重写
        :param keyword: 关键词
        :param page: 页号
        :return: 包含结果的二维列表/查询失败则返回布尔值
        """
        return False

    def get_music_url(self, music_id: StrInt) -> str:
        """
        获取音乐url，需要重写
        :param music_id: 音乐id
        :return: 音乐url
        """
        return ""

    def get_album_info(self, album_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str]]]:
        """
        获取专辑信息，需要重写
        :param album_id: 专辑id
        :return: 专辑信息(专辑名称, 艺术家名称, [(歌曲id，歌曲名称), ...])
        """
        pass

    @staticmethod
    def is_song_list_url(keyword) -> StrInt:
        """
        判断是否为歌单链接，需要重写
        :param keyword: 链接
        :return: 歌单id
        """
        return ''

    def get_song_list_info(self, song_list_id: StrInt) -> Tuple[str, str, List[Tuple[StrInt, str, str, StrInt, str]]]:
        """
        从歌单链接获取歌单信息，需要重写
        :param song_list_id: 歌单链接
        :return: 查询结果(歌单名称、创建者、[(歌曲id, 歌曲名称, 艺术家名称, 专辑id, 专辑名称), ...])
        """
        pass

    def _download_song_list(self, song_list_id: StrInt) -> None:
        """
        下载歌单函数，无需重写，这个函数把从歌单获取到的歌曲下载下来
        :param song_list_id: 歌单id
        :return None
        """
        song_list_name, song_list_creator, song_list_info = self.get_song_list_info(song_list_id)
        while True:
            print_song_list(song_list_info, song_list_name, song_list_creator)
            music_cnt = len(song_list_info)
            choice = my_input(f"[input] 请输入序号选择([0]~{music_cnt * 2 + 1})：", t=int, min_val=0, max_val=music_cnt * 2 + 1, default=0)
            if choice == 0:
                clear_screen()
                break
            elif 1 <= choice <= music_cnt:
                download = my_input(f"[Input] 是否下载{song_list_info[choice - 1][1]}-{song_list_info[choice - 1][2]}？([1]/0)：", t=bool, default=True)
                if download:
                    clear_screen()
                    self._download_music(song_list_info[choice - 1][0], song_list_info[choice - 1][1])
                else:
                    clear_screen()
            elif music_cnt + 1 <= choice <= music_cnt * 2:
                clear_screen()
                self._download_album(song_list_info[choice - music_cnt - 1][3])
            elif choice == music_cnt * 2 + 1:
                download = my_input(f"[input] 是否下载歌单中的全部歌曲？([1]/0)：", t=bool, default=True)
                clear_screen()
                if download:
                    for i in range(music_cnt):
                        music_id = song_list_info[i][0]
                        music_name = song_list_info[i][1]
                        artist_name = song_list_info[i][2]
                        self._download_music(music_id, music_name, artist_name, i == music_cnt - 1)
                    if not self.download_queue.empty():
                        self._download_start()

    def _download_music(self, music_id: StrInt, music_name: str, artist_name: str = "", download_now: bool = True) -> None:
        """
        下载音乐函数，无需重写，这个函数将获取的音乐url和音乐名称和艺术家保存到下载队列中
        :param music_id: 音乐id
        :param music_name: 音乐名称
        :param artist_name: 艺术家名称
        :param download_now: 是否立即下载
        :return: None
        """
        if not os.path.exists(self.music_dir):
            os.mkdir(self.music_dir)
        if self.save_artist:
            music_path = os.path.join(self.music_dir, f"{music_name} - {artist_name}.{self.ext}")
        else:
            music_path = os.path.join(self.music_dir, f"{music_name}.{self.ext}")
        if os.path.exists(music_path):
            my_print(f"[Error] {music_path} 已存在，下载终止。", color="red", highlight=True)
            return
        music_url = self.get_music_url(music_id)
        if not music_url:
            my_print(f"[Error] 因为版权原因无法获取 {music_name} 的下载链接，下载终止。", color="red", highlight=True)
            return
        self.download_queue.put((music_url, music_name, artist_name))
        if download_now:
            self._download_start()

    def _download_album(self, album_id: StrInt) -> None:
        """
        下载专辑函数，无需重写，这个函数把下载的音乐url和音乐名称和艺术家放置于下载队列中
        :param album_id: 专辑id
        :return: None
        """
        album_name, artist_name, album_info = self.get_album_info(album_id)
        print_album(album_info, album_name, artist_name)
        music_cnt = len(album_info)
        choice = my_input(f"[input] 请输入序号选择([0]~{music_cnt + 1})：", t=int, min_val=0, max_val=music_cnt + 1, default=0)
        if choice == 0:
            clear_screen()
        elif 1 <= choice <= music_cnt:
            music_id = album_info[choice - 1][0]
            music_name = album_info[choice - 1][1]
            download = my_input(f"[input] 是否下载 {music_name} ？([1]/0)：", t=bool, default=True)
            if download:
                self._download_music(music_id, music_name, artist_name)
            else:
                clear_screen()
        else:
            download = my_input(f"[input] 是否下载专辑中的全部歌曲？([1]/0)：", t=bool, default=True)
            clear_screen()
            if download:
                for i in range(music_cnt):
                    music_id = album_info[i][0]
                    music_name = album_info[i][1]
                    self._download_music(music_id, music_name, artist_name, i == music_cnt - 1)
                if not self.download_queue.empty():
                    self._download_start()

    def _download_start(self) -> None:
        """
        使用多进程下载的函数
        :return: None
        """
        t1 = time.time()
        processes = []
        for i in range(self.max_process):
            p = mp.Process(target=self._download_process)
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        t2 = time.time()
        my_print(f"[Info] 下载用时：{t2 - t1}秒。", color="magenta")

    def _download_process(self) -> None:
        """
        多进程下载任务
        :return: None
        """
        while not self.download_queue.empty():
            music_info = self.download_queue.get(block=False)
            music_url = music_info[0]
            music_name = music_info[1]
            artist_name = music_info[2]
            music_name = self._sanitize_filename(music_name)
            artist_name = self._sanitize_filename(artist_name)
            if self.save_artist:
                music_path = os.path.join(self.music_dir, f"{music_name} - {artist_name}.{self.ext}")
            else:
                music_path = os.path.join(self.music_dir, f"{music_name}.{self.ext}")
            music_response = requests.get(music_url, headers=self.headers)
            with open(music_path, 'wb') as music_file:
                music_file.write(music_response.content)
            my_print(f"[Success] {music_name} 保存成功。", color="green", highlight=True)

    def _sanitize_filename(self, filename):
        return re.sub(self.illegal_chars, '_', filename)
