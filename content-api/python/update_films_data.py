#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.error import URLError, HTTPError
import logging
import datetime
try:
    from client import SmartyContentAPI, ContentAPIException
except ImportError:
    raise ImportError('client.py file not found')


smarty_url: str = 'http://127.0.0.1:8180/' # Ссылка на Smarty
content_api_key: str = 'api_key' # ContentAPI ключ. Нужен для обновления
client_id: int = 1


class ParseError(Exception):
    pass


class UpdateVideoList(object):
    def __init__(self, api, videos_per_page):
        self.api = api
        self.videos_per_page = videos_per_page

    def get_pages(self, limit: int, count: int):
        pages = count//limit
        if count % limit != 0:
            pages += 1
        return pages

    def update_video(self, video_files: int):
        try:
            api.video_modify(id=video_files, load_meta=1)
        except URLError or HTTPError:
            ParseError()

    def update_content(self, videos):
        for video in videos:
            video_files = video['id']
            try:
                self.update_video(video_files)
                print(f'Информация о фильме с ID = {video_files} обновлена успешно')
                logging.info(f'Информация о фильме с ID = {video_files} обновлена успешно')
            except ContentAPIException as error:
                print(f'Произошла ошибка при обновлении информации медиатеки для фильма/сериала {video_files}.'
                      f' Для уточнения откройки последний лог-файл')
                logging.error(f'Произошла ошибка при обновлении информации медиатеки для фильма/сериала {video_files}.'
                              f' Сообщение об ошибки: {repr(error)}')
                break

    def load_data(self):
        # videos_per_page = 5
        response = self.api.video_list(page=1, limit=self.videos_per_page)
        self.update_content(response['videos'])
        if response['count'] > self.videos_per_page:
            pages = self.get_pages(self.videos_per_page, response['count'])
            for i in range(2, pages+1):
                response = self.api.video_list(page=i, limit=self.videos_per_page)
                self.update_content(response['videos'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename=f"update_media_list_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    api = SmartyContentAPI(smarty_url, client_id, content_api_key)
    update_videos = UpdateVideoList(api, videos_per_page=1) # Примечание: можно в videos_per_page указать количество фильмов на страницу от 1 до 100
    update_videos.load_data()
