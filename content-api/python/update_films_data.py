#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import datetime
try:
    from client import SmartyContentAPI
except ImportError:
    raise ImportError('client.py file not found')


smarty_url: str = 'http://127.0.0.1:8180/' # Ссылка на Smarty
content_api_key: str = 'api_key' # ContentAPI ключ. Нужен для обновления
client_id: int = 1


class UpdateVideoList(object):
    """Класс, представляющий собой обновление метаданных фильмов и сериалов в Smarty.

    Note:
        Для работоспособности скрипта требуется чтобы в Smarty у фильма/сериала было вбито в поле "ID фильма на кинопоиске" само ID поле.
    """
    def __init__(self, api: SmartyContentAPI):
        self.api = api

    def _get_pages(self, limit: int, count: int):
        pages = count // limit
        if count % limit != 0:
            pages += 1
        return pages

    def _update_video(self, video_files: int):
        api.video_modify(id=video_files, load_meta=1)

    def _update_content(self, videos):
        for video in videos:
            video_files = video['id']
            try:
                self._update_video(video_files)
                print(f'Информация о фильме с ID = {video_files} обновлена успешно')
                logging.info(f'Информация о фильме с ID = {video_files} обновлена успешно')
            except Exception as error:
                print(f'Произошла ошибка при обновлении информации медиатеки для фильма/сериала {video_files}.'
                      f' Для уточнения откройки последний лог-файл')
                logging.error(f'Произошла ошибка при обновлении информации медиатеки для фильма/сериала {video_files}.'
                              f' Сообщение об ошибки: {repr(error)}')
                continue

    def run(self):
        """Запуск скрипта обновления метаданных фильмов и сериалов в Smarty."""
        videos_per_page: int = 1
        response = self.api.video_list(page=1, limit=videos_per_page)
        self._update_content(response['videos'])
        if response['count'] > videos_per_page:
            pages = self._get_pages(videos_per_page, response['count'])
            for i in range(2, pages + 1):
                response = self.api.video_list(page=i, limit=videos_per_page)
                self._update_content(response['videos'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename=f"update_media_list_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    api = SmartyContentAPI(smarty_url, client_id, content_api_key)
    update_videos = UpdateVideoList(api)
    update_videos.run()
