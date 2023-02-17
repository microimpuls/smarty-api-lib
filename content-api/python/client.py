# -*- coding: utf-8 -*-
import json
import urllib.parse
import hashlib
import base64
import urllib.request
import urllib.error
import urllib
from datetime import datetime

class ContentAPIException(Exception):
    pass


class SmartyContentAPI(object):
    def __init__(self, base_url, client_id, api_key):
        """
        :param base_url: хост smarty, например http://smarty.microimpuls.com
        :param client_id: идентефикатор клиента
        :param api_key: ключ клиента
        """
        self.base_url = base_url
        self.client_id = client_id
        self.api_key = api_key

    def _get_signature(self, request_data):
        sign_source = u''
        for (key, value) in sorted(request_data.items()):
            sign_source += u'%s:%s;' % (key, value)
        sign_source += self.api_key
        digester = hashlib.md5()
        sign_source_utf = sign_source.encode('utf-8')
        sign_source_base64 = base64.b64encode(sign_source_utf)
        digester.update(sign_source_base64)
        signature = digester.hexdigest()
        return signature

    def _get_full_url(self, path):
        parsed_base_url = urllib.parse.urlparse(self.base_url)
        full_url = urllib.parse.urlunparse(parsed_base_url._replace(path=path))
        return full_url

    def _api_request(self, path, data=None):
        url = self._get_full_url(path)
        data = data or {}
        data['client_id'] = self.client_id
        data['signature'] = self._get_signature(data)
        encoded_post_data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, encoded_post_data)
        response = urllib.request.urlopen(req)
        api_response = json.loads(response.read())
        if api_response['error']:
            error_message = "Api Error %(error)s: %(error_message)s" % api_response
            raise ContentAPIException(error_message)
        return api_response

    @staticmethod
    def _set_params(params, fields, kwargs):
        for key, value in kwargs.items():
            if key in fields:
                params[key] = value

# VIDEO
    def video_create(self, name, rating, **kwargs):
        params = {
            'name': name,
            'rating': rating,
        }
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5', 'name_orig',
            'description', 'description_lang1', 'description_lang2', 'description_lang3', 
            'description_lang4', 'description_lang5', 'year', 'countries', 'countries_lang1', 
            'countries_lang2', 'countries_lang3', 'countries_lang4', 'countries_lang5', 
            'director', 'director_lang1', 'director_lang2', 'director_lang3', 'director_lang4', 
            'director_lang5', 'genres_kinopoisk', 'uri', 'language', 'language_lang1', 
            'language_lang2', 'language_lang3', 'language_lang4', 'language_lang5', 'ext_id', 
            'premiere_date', 'published_from', 'published_to', 'copyright_holder', 
            'external_api_config', 'price_category', 'video_provider', 'genres', 'stream_services', 
            'tariffs', 'actors_set', 'available_on', 'package_videos', 'kinopoisk_rating',
            'imdb_rating', 'average_customers_rating', 'duration', 'parent_control', 
            'is_announcement'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/video/create/', params)

    def video_list(self, limit, page):
        params = {
            'limit': limit,
            'page': page,
        }
        return self._api_request('/content/api/video/list/', params)

    def videofile_create(self, name, vid, **kwargs):
        params = {
            'name': name,
            'vid': vid
        }
        fields = [
            'episode_id', 'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 
            'name_lang5', 'filename', 'duration', 'is_trailer', 'ext_id', 'sort_after_vfid', 
            'quality'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/video/file/create/', params)

    def video_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/video/delete/', params)

    def video_modify(self, id, **kwargs):
        params = {'id': id}
        fields = [
            'load_meta', 'kinopoisk_id', 'name_lang1', 'name_lang2', 'name_lang3', 
            'name_lang4', 'name_lang5', 'name_orig', 'director', 'director_lang1', 
            'director_lang2', 'director_lang3', 'director_lang4', 'director_lang5', 
            'countries', 'countries_lang1', 'countries_lang2', 'countries_lang3', 
            'countries_lang4', 'countries_lang5', 'description', 'description_lang1', 
            'description_lang2', 'description_lang3', 'description_lang4', 'description_lang5', 
            'year', 'poster_url', 'screenshot_url', 'actors_set', 'genres_kinopoisk', 
            'kinopoisk_rating', 'imdb_rating', 'rating', 'duration'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/video/modify/', params)

    def videofile_modify(self, id, **kwargs):
        params = {'id': id}
        fields = [
            'name', 'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 
            'name_lang5', 'filename', 'is_trailer', 'duration', 'episode_id', 'quality'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/video/file/modify/', params)

# SEASON
    def season_create(self, name, vid, **kwargs):
        params = {
            'name': name,
            'vid': vid
        }
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 
            'name_lang4', 'name_lang5', 'sort_after_sid'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/season/create/', params)

    def season_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/season/delete/', params)

    def season_modify(self, season_id, **kwargs):
        params = {
            'season_id': season_id
        }
        fields = [
            'name', 'name_lang1', 'name_lang2', 'name_lang3', 
            'name_lang4', 'name_lang5', 'sort_after_sid'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/season/modify/', params)

# EPISODE
    def episode_create(self, vid, name, **kwargs):
        params = {
            'vid': vid,
            'name': name
        }
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5',
            'description', 'description_lang1', 'description_lang2', 'description_lang3',
            'description_lang4', 'description_lang5', 'duration', 'season_id',
            'sort_after_eid'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/episode/create/', params)

    def episode_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/episode/delete/', params)

    def episode_modify(self, episode_id, **kwargs):
        params = {
            'episode_id': episode_id
        }
        fields = [
            'name', 'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 
            'name_lang5', 'description', 'description_lang1', 'description_lang2', 
            'description_lang3', 'description_lang4', 'description_lang5', 'duration', 
            'sort_after_eid'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/episode/modify/', params)

# CHANNEL
    def channel_create(self, name, rating, **kwargs):
        params = {
            'name': name,
            'rating': rating,
            'recording_days': 0
        }
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5', 
            'hbb_channel_pid', 'uri', 'url_prefix', 'multicast_address', 
            'secondary_multicast_address', 'id_for_stream_service', 'comment', 
            'version', 'option1', 'option2', 'option3', 'telemeter_account_name', 
            'telemeter_tmsec_name', 'telemeter_cat_id', 'telemeter_vc_id', 
            'telemeter_vc_version', 'mediahills_id', 'pause_live_tv_shift', 'lcn_number', 
            'recording_days', 'telemeter', 'aspect_ratio', 'show_in_all', 'parent_control', 
            'enabled', 'display_on_site', 'category', 'epg_channel', 'copyright_holder', 
            'price_category', 'sort_after_cid', 'additional_categories', 'tariffs', 
            'stream_services', 'hbb_providers'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/channel/create/', params)

    def channel_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/channel/delete/', params)

#SEANCE
    def seance_create(self, vid, date_start, **kwargs):
        params = {
            'vid': vid,
            'date_start': date_start
        }
        fields = [
            'vfid', 'date_end'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/seance/create/', params)

    def seance_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/seance/delete/', params)

    def seance_ticket_create(self, sid, **kwargs):
        params = {'sid': sid}
        fields = ['code']
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/seance/ticket/create/', params)

    def seance_ticket_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/seance/ticket/delete/', params)

#RADIO
    def radio_create(self, name, **kwargs):
        params = {'name': name}
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5', 
            'enabled', 'tariffs', 'uri', 'description', 'description_lang1', 
            'description_lang2', 'description_lang3', 'description_lang4', 
            'description_lang5', 'radio_channel'
        ]

        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/radio/create/', params)

    def radio_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/radio/delete/', params)

#EPGPROGRAM
    #???
    def epg_program_time_specify(self, external_id, start, stop):
        params = {
            'external_id': external_id,
            'start': start,
            'stop': stop
        }
        return self._api_request('/content/api/epg/program/time/specify/', params)

#CAMERA
    def camera_create(self, name, **kwargs):
        params = {'name': name}
        fields = [
            'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 'name_lang5', 
            'category', 'additional_categories', 'enabled', 'sort_after_cid', 'epg_channel', 
            'tariffs', 'stream_services', 'uri', 'url_prefix', 'price_category', 
            'multicast_address', 'secondary_multicast_address', 'id_for_stream_service', 
            'comment', 'option1', 'option2', 'option3'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/camera/create/', params)

    def camera_modify(self, camera_id, **kwargs):
        params = {'camera_id': camera_id}
        fields = [
            'name', 'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 
            'name_lang5', 'enabled', 'tariffs', 'stream_services', 'uri', 
            'url_prefix', 'multicast_address', 'price_category'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/camera/modify/', params)

    def camera_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/camera/delete/', params)

#ACTOR
    def actor_create(self, **kwargs):
        params = {}
        fields = [
            'name', 'name_lang1', 'name_lang2', 'name_lang3', 'name_lang4', 
            'name_lang5', 'birthdate', 'gender', 'country', 'country_lang1', 
            'country_lang2', 'country_lang3', 'country_lang4', 'country_lang5', 
            'profession', 'profession_lang1', 'profession_lang2', 'profession_lang3', 
            'profession_lang4', 'profession_lang5', 'biography', 'biography_lang1', 
            'biography_lang2', 'biography_lang3', 'biography_lang4', 'biography_lang5', 
            'name_orig', 'movie_db_id'
        ]
        self._set_params(params, fields, kwargs)
        return self._api_request('/content/api/actor/create/', params)

    def actor_delete(self, id):
        params = {'id': id}
        return self._api_request('/content/api/actor/delete/', params)



api = SmartyContentAPI(base_url='http://smarty.example.com/', client_id=1, api_key='top secret')
#print(api.video_create('baruto_6', 0, kinopoisk_rating=10, year=2022))
#print(api.season_create('season3', '316225', sort_after_sid=13093))
#print(api.episode_create(316225, '1', season_id=13093))
#print(api.videofile_create('file_1', 316225, episode_id=254950))
#print(api.channel_create('ani', 0))
#print(api.channel_delete(390))
#print(api.season_delete(13094))
#print(api.season_modify(13095, name='season 4'))
#print(api.episode_delete(254950))
#print(api.episode_modify(254949, name='test_prev', duration=120))
#print(api.video_delete(316226))
#print(api.video_modify(316225, director='god'))
#print(api.videofile_modify(12426331, is_trailer=1))
#print(api.seance_create(316225, datetime(2022, 11, 6, 12, 30, 0).isoformat(), date_end=datetime(2022, 12, 6, 12, 30, 0).isoformat()))
#print(api.seance_delete(20))
#print(api.seance_ticket_create(21))
#print(api.seance_ticket_delete(21))
#print(api.radio_create('ani_rad'))
#print(api.radio_delete(54))
#print(api.camera_create('test_cam'))
#print(api.camera_modify(28, enabled=0))
#print(api.camera_delete(28))
#print(api.actor_create(name='billibil qwe', country='mars', movie_db_id=4002834))
#print(api.actor_delete(451593))
