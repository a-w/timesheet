# -*- coding: utf-8 -*-
# Copyright 2021 Adrian Weiler. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Timeular API interface for the time sheet evaluator.

Reference: https://developers.timeular.com/
"""

import json
import os

import requests

from .entry import CalendarEntry

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


class _Session:
    def __init__(self, url, calendar: dict, config_dir):
        self._url = url
        self._calendar = calendar
        self._token = None
        self._token_file = os.path.join(config_dir, "token.json")
        self._user_info = None
        try:
            with open(self._token_file, 'r', encoding='utf-8') as _:
                self._token = json.load(_)
        except (IOError, json.decoder.JSONDecodeError):
            self._token = None

    def renew_token(self):
        result = self.post('developer/sign-in', self._calendar['api'])
        self._token = result['token']
        if self._calendar.get('persist_token', True):
            with open(self._token_file, 'w', encoding='utf-8') as _:
                json.dump(self._token, _)

    def __enter__(self):
        try:
            self.get_user_info()
        except requests.HTTPError as e:
            print('Requesting a new token...')
            self.renew_token()
            # Try again
            self.get_user_info()
        print (f'Authenticated as {self._user_info["name"]}')
        return self

    def get_user_info(self):
        me = self.get('me')
        self._user_info = me['data']

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If we already had an HTTP error, don't attempt anything anymore
        if isinstance(exc_val, requests.HTTPError):
            return

        if not self._calendar.get('persist_token', True):
            self.post('developer/logout', self._calendar['api'])

    def get(self, endpoint):
        """
        Perform a POST operation on the API

        :param endpoint: The endpoint to query
        :return: The response as dictionary
        """
        response = requests.get(url=f'{self._url}{endpoint}', headers=dict(
            Authorization=f'Bearer {self._token}'))
        response.raise_for_status()

        return response.json()

    def post(self, endpoint, data):
        """
        Performs a POST operation on the API
        :param endpoint: The endpoint to query
        :param data: dict with data to pass as JSON data
        :return: The response as dictionary, if any, None otherwise
        """
        headers = dict()
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'

        response = requests.post(url=f'{self._url}{endpoint}', json=data, headers=headers)
        response.raise_for_status()

        # noinspection PyBroadException
        try:
            return response.json()
        except Exception:
            # Logout doesn't return any data, that's OK
            return None


class Provider:
    """
    Calendar provider for the Timeular API
    """

    def __init__(self, config, _flags):
        self._url = config["url"]
        self._config_dir = config["config_dir"]
        self._tz = config.get("tz", "utc")

    def get_calendar(self, name):
        """
        Access the named calendar.

        This implementations reads a json file with the name of the calendar and returns its contents
        parsed to a dict. This json file must have a key `api` containing a dict with the
        keys `apiKey` and `apiSecret`.

        :param name: The name of the calendar
        :return: The contents of the json file describing the calendar as dict
        """
        calendar_config = os.path.join(self._config_dir, f'{name}.json')

        with open(calendar_config, 'r', encoding='utf-8') as _:
            return json.load(_)

    def read_entries(self, calendar, start_date, end_date, parse):
        """
        Generator to read entries from the named calendar

        :param calendar: The name of the calendar
        :param start_date: The start date
        :param end_date: The end date
        :param parse: callback to parse a calendar entry
        :return: None, yields entries instead
        """
        time_min = start_date.isoformat() + "T00:00:00.000"
        time_max = end_date.isoformat() + "T00:00:00.000"

        with _Session(self._url, calendar, self._config_dir) as s:
            activities = dict((a['id'], parse(a['name'])) for a in s.get('activities')['activities'])
            entries = s.get(f'time-entries/{time_min}/{time_max}')

        for entry in entries['timeEntries']:
            activity_id = entry['activityId']
            activity = activities.get(activity_id)
            project_key = activity[1]
            if project_key is None:
                continue

            yield CalendarEntry(entry, activity, self._tz), project_key
