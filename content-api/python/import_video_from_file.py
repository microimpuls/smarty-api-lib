#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import openpyxl # pip install openpyxl, for parsing xlsx
try:
    from client import SmartyContentAPI
except ImportError:
    raise ImportError("client.py file not found")

SERVER_HOST = 'http://127.0.0.1:8000'
API_KEY = 'ofYI09U9jsI7EhNCYsJ0l56eYgAPgfFr' # Content API key
CLIENT_ID = 1

class Import_video_from_file():
    def __init__(self, api, file_path: str):
        self.api = api
        self.file_path = file_path

        if self.file_path.split('.')[-1] == "csv":
            self.parse_csv()
        elif self.file_path.split('.')[-1] == "xlsx":
            self.parse_xlsx()
        else:
            print("Excaptions: type file not a .csv or .xlsx")

    def parse_csv(self):
        # parsing csv
        kwargs = {}
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.pop('Name')
                rating = row.pop('Rating')
                if not name or not rating:
                    print("Excaption: not name or rating!")
                    continue
                for key, value in row.items():
                    kwargs[key] = value
                print(self.api.video_create(name, rating, **kwargs))

    def parse_xlsx(self):
        # parsing xlsx
        wookbook = openpyxl.load_workbook(self.file_path)
        worksheet = wookbook.active
        kwargs = {}
        for i in range(1, worksheet.max_row):
            for col in worksheet.iter_cols(1, worksheet.max_column):
                if col[i].value and col[0].value:
                    kwargs[col[0].value] = col[i].value
            name = kwargs.pop('Name')
            rating = kwargs.pop('Rating')
            print(self.api.video_create(name, rating, **kwargs))
            kwargs.clear()

    pass

if __name__ == "__main__":
    api = SmartyContentAPI(SERVER_HOST, CLIENT_ID, API_KEY)
    input_file = 'client_1_services_videos_2023_03_06T16_40_29.csv'
    Import_video_from_file(api, input_file)