#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Additional re module required for regular expressions."""
import re
try:
    from client import SmartyContentAPI
except ImportError:
    raise ImportError("client.py file not found")


SERVER_HOST = 'http://127.0.0.1:8000'
API_KEY = 'api_key' # Content API key
CLIENT_ID = 1
VIDEO_FILE_REGEX = r'^Сезон (\d+) Серия (\d+)$'


class ParseError(Exception):
    pass


class Season(object):
    def __init__(self, api, season_number=None, vid=None):
        self.api = api
        self.name = "Сезон {0}".format(season_number)
        self.vid = vid

    def create(self):
        return api.season_create(self.name, self.vid)['id']


class Episode(object):
    def __init__(self, api, season_number=None, episode_number=None, vid=None, season_id=None, duration=None):
        self.api = api
        self.name = "Сезон {0} Серия {1}".format(season_number, episode_number)
        self.vid = vid
        self.season_id = season_id
        self.duration = duration

    def create(self):
        return api.episode_create(self.vid, self.name, season_id=self.season_id, duration=self.duration)['id']


class VideoFile(object):
    def __init__(self, api, id=None, name=None, vid=None, episode_id=None, duration=None):
        self.api = api
        self.id = id
        self.name = name
        self.vid = vid
        self.episode_id = episode_id
        self.duration = duration//60

    def modify(self):
        api.videofile_modify(
            id=self.id,
            episode_id=self.episode_id,
        )


class SyncContent(object):
    def __init__(self, api):
        self.api = api
        self.seasons = {}
        self.episodes = {}

    def get_pages(self, limit, count):
        pages = count//limit
        if count % limit != 0:
            pages += 1
        return pages

    def is_updated(self, video):
        return video['has_seasons'] and video['has_episodes']

    def parse_vf_name(self, vf_name):
        match = re.match(VIDEO_FILE_REGEX, vf_name)
        if match and len(match.group(0)) == len(vf_name):
            season_number = int(match.group(1))
            episode_number = int(match.group(2))
            return season_number, episode_number
        raise ParseError

    def create_season(self, season_number, vf_vid):
        if season_number not in self.seasons.keys():
            s = Season(self.api, season_number, vf_vid)
            self.seasons[season_number] = s.create()

    def create_episode(self, season_number, episode_number, vf):
        if vf.name not in self.episodes.keys():
            season_id = self.seasons[season_number]
            e = Episode(self.api, season_number, episode_number, vf.vid, season_id, vf.duration)
            self.episodes[vf.name] = e.create()
        vf.episode_id = self.episodes[vf.name]

    def update_videofile(self, vf, vid):
        vf_obj = VideoFile(
            self.api,
            id=vf['id'],
            name=vf['name'],
            vid=vid,
            duration=vf['duration']
        )
        try:
            season_number, episode_number = self.parse_vf_name(vf_obj.name)
        except ParseError:
            print("WARN: Parsing error video_id={0}, videofile_id={1}".format(vid, vf_obj.id))
            return False
        self.create_season(season_number, vf_obj.vid)
        self.create_episode(season_number, episode_number, vf_obj)
        vf_obj.modify()
        return True

    def update_content(self, videos):
        for video in videos:
            self.seasons = {}
            self.episodes = {}
            if self.is_updated(video):
                continue
            video_files = video['files']
            is_success = True
            for vf in video_files:
                is_success = self.update_videofile(vf, video['id']) and is_success
            if video_files and is_success:
                print("Video id={} updated successfully".format(video['id']))
            elif video_files:
                print("Video id={} update failed".format(video['id']))

    def load_data(self):
        limit = 100
        response = self.api.video_list(page=1, limit=limit)
        self.update_content(response['videos'])
        if response['count'] > limit:
            pages = self.get_pages(limit, response['count'])
            for i in range(2, pages+1):
                response = self.api.video_list(page=i, limit=limit)
                self.update_content(response['videos'])


if __name__ == "__main__":
    api = SmartyContentAPI(SERVER_HOST, CLIENT_ID, API_KEY)
    sync_content = SyncContent(api)
    sync_content.load_data()
