# -*- coding: utf-8 -*
from client import SmartyContentAPI, ContentAPIException

from urllib.error import URLError, HTTPError

import logging
import datetime

smarty_url = 'http://example.com/'  # Ссылка на Smarty
client_id = 1  # ID клиента Smarty
content_api_key = 'top secret'  # ContentAPI ключ. Нужно для обновления данных о фильмах


def get_from_smarty_films_in_the_form_json_list(page):
    limit_film = 100 # Количество фильмов/Сериалов на одну страницу
    number = 0

    get_api_response = api.video_list(limit=limit_film, page=page)
    video_count = get_api_response['count'] # Получение сколько всего фильмов/сериалов
    videos_info = get_api_response['videos'] # Получение данных о фильме
    get_from_smarty_films_data(videos_info, video_count, number, page, limit_film)


def get_from_smarty_films_data(videos_info, video_count, number, page, limit_film):
    while video_count > page:
        try:
            id_number = videos_info[number]['id'] # Получение ID фильма
            try:
                api.video_modify(id=id_number, load_meta=1) # Обновление данных фильма (требуется вбитый kinopoisk_id в Smarty)
                logging.info(
                    f"Для фильма/сериала с ID {id_number} была обновлена информация через Kinopoisk Unofficial "
                    f"API и добавлена в Smarty.")
            except HTTPError or URLError or IndexError:
                logging.error(f"Ошибка при обновлении данных о фильме {id_number}. Пропускаем...", exc_info=True)
                pass
            number += 1
            if number == limit_film:
                page += 1
                get_from_smarty_films_in_the_form_json_list(page)
        except IndexError or HTTPError or URLError or ContentAPIException:
            logging.error('Незивеста ошибка! Ошибка: ', exc_info=True)
            break


if __name__ == '__main__':
    api = SmartyContentAPI(base_url=smarty_url, client_id=client_id, api_key=content_api_key)
    logging.basicConfig(level=logging.INFO,
                        filename=f"SmartyKinopoisk_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    get_from_smarty_films_in_the_form_json_list(page=1)
