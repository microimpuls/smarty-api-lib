#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Sync all videos: python3 sync_content.py

Sync videos by id: python3 sync_content.py --video 1

Or sync some videos by id: python3 sync_content.py --video 1 2 3 4 5 6
"""
import argparse
import datetime
import logging
import re
try:
    from client import SmartyContentAPI
except ImportError:
    raise ImportError('client.py file not found')


SERVER_HOST = 'http://127.0.0.1:8000'
API_KEY = 'api_key'  # Content API key
CLIENT_ID = 1
VIDEO_ID = 1  # ID for sync_video(id: int) method
VIDEO_FILE_REGEX = r'^Сезон (\d+) Серия (\d+)$'

# if True videos that already have seasons but have no episodes or vice versa will be skipped.
CAREFUL_DUBLICATES_CHECK = True


class ParseError(Exception):
    pass


class Season(object):
    def __init__(self, api, season_number=None, vid=None):
        self.api = api
        self.name = 'Сезон {0}'.format(season_number)
        self.vid = vid

    def create(self):
        return api.season_create(self.name, self.vid)['id']


class Episode(object):
    def __init__(self, api, episode_number=None, vid=None, season_id=None, duration=None):
        self.api = api
        self.name = 'Серия {0}'.format(episode_number)
        self.vid = vid
        self.season_id = season_id
        self.duration = duration

    def create(self):
        return api.episode_create(
            vid=self.vid, name=self.name,
            season_id=self.season_id, duration=self.duration,
        )['id']


class VideoFile(object):
    def __init__(self, api, id=None, name=None, vid=None, episode_id=None, duration=None):
        self.api = api
        self.id = id
        self.name = name
        self.vid = vid
        self.episode_id = episode_id
        self.duration = duration // 60

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
        self.total_updated = 0

    def create_season(self, season_number: int, vf_vid: int):
        if season_number not in self.seasons.keys():
            s = Season(self.api, season_number, vf_vid)
            self.seasons[season_number] = s.create()

    def create_episode(self, season_number: int, episode_number: int, vf: VideoFile):
        if vf.name not in self.episodes.keys():
            season_id = self.seasons[season_number]
            e = Episode(
                api=self.api,
                episode_number=episode_number,
                vid=vf.vid,
                season_id=season_id,
                duration=vf.duration,
            )
            self.episodes[vf.name] = e.create()
        vf.episode_id = self.episodes[vf.name]

    def parse_vf_name(self, vf_name: str):
        match = re.match(VIDEO_FILE_REGEX, vf_name)
        if match and len(match.group(0)) == len(vf_name):
            season_number = int(match.group(1))
            episode_number = int(match.group(2))
            return season_number, episode_number
        raise ParseError

    def update_videofile(self, vf: dict, vid: int) -> bool:
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
            log_ctx = {
                'video_id': vid,
                'videofile_name': vf_obj.name,
                'videofile_id': vf_obj.id,
            }
            logging.warning('videofile name parsing error', extra={'ctx': log_ctx})
            return False
        self.create_season(season_number, vf_obj.vid)
        self.create_episode(season_number, episode_number, vf_obj)
        vf_obj.modify()
        return True

    def try_to_process_videofiles(self, video: dict) -> bool:
        video_files = video['files']
        if not video_files:
            return False

        video_id = video['id']
        has_updations = False
        for vf in video_files:
            is_video_updated = self.update_videofile(vf, video_id)
            if is_video_updated:
                has_updations = True
        return has_updations

    def set_video_is_season_status(self, video: dict, is_season: bool):
        api.video_modify(video['id'], is_season=is_season)

    def update_content(self, videos: list):
        for video in videos:
            self.update_video(video)

    def init_dicts_to_check_no_dublication(self):
        self.seasons = {}
        self.episodes = {}

    def is_updated(self, video: dict) -> bool:
        if CAREFUL_DUBLICATES_CHECK:
            return video['has_seasons'] or video['has_episodes']
        return video['has_seasons'] and video['has_episodes']

    def update_video(self, video: dict) -> bool:
        """
        Returns True if video sucessfully updated
        """
        log_ctx = {'video_id': video['id']}
        if self.is_updated(video):
            logging.debug('already updated', extra={'ctx': log_ctx})
            return False

        self.init_dicts_to_check_no_dublication()

        is_successfully_updated = self.try_to_process_videofiles(video)
        if is_successfully_updated:
            self.set_video_is_season_status(video, True)
            self.total_updated += 1
            logging.debug('success', extra={'ctx': log_ctx})
        else:
            logging.warning('failed', extra={'ctx': log_ctx})

        return is_successfully_updated

    def sync_all_videos(self):
        self.total_updated = 0
        log_ctx = {'client_id': CLIENT_ID}
        logging.info('start', extra={'ctx': log_ctx})

        limit = 100
        page = 1
        while True:
            response = self.api.video_list(page=page, limit=limit)
            if not response['videos']:
                break
            self.update_content(response['videos'])
            page += 1
        log_ctx.update(updated_videos_count=self.total_updated)
        logging.info('finish', extra={'ctx': log_ctx})

    def get_video(self, video_id: int) -> 'dict|None':
        limit = 100
        page = 1
        while True:
            response = self.api.video_list(page=page, limit=limit)
            if not response['videos']:
                break
            for video in response['videos']:
                if video['id'] == video_id:
                    return video
            page += 1
        return None

    def sync_video(self, video_id: int):
        log_ctx = {'client_id': CLIENT_ID, 'video_id': video_id}
        logging.info('start', extra={'ctx': log_ctx})

        video = self.get_video(video_id)
        if video:
            self.update_video(video)
        else:
            logging.warning('video does not exist', extra={'ctx': log_ctx})


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename=f'sync_content_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
        filemode='w',
        format='%(asctime)s [%(levelname)s] %(funcName)s - %(message)s - params=%(ctx)s',
    )
    api = SmartyContentAPI(SERVER_HOST, CLIENT_ID, API_KEY)
    sync_content = SyncContent(api)

    parser = argparse.ArgumentParser()
    parser.add_argument('--video', nargs='+', type=int, help='video ids list separated by space')
    args = parser.parse_args()

    video_ids = args.video
    if video_ids:
        for video_id in video_ids:
            sync_content.sync_video(video_id)
    else:
        sync_content.sync_all_videos()
