# -*- coding: utf-8 -*-
# Copyright 2018 Adrian Weiler. All Rights Reserved.
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

"""Google Calendar API interface for the time sheet evaluator."""

import os
import sys

from googleapiclient import discovery
from googleapiclient.http import build_http
from oauth2client import client, file, tools

from .entry import CalendarEntry

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


class Provider:
    def __init__(self, config, flags):
        provider_path = os.path.dirname(__file__)

        name = config.get("name", "calendar")
        scope = config.get("scope", "https://www.googleapis.com/auth/" + name)
        version = config.get("version", "v3")
        self._tz = config.get("tz", "utc")

        # Name of a file containing the OAuth 2.0 information for this
        # application, including client_id and client_secret, which are found
        # on the API Access tab on the Google APIs
        # Console <http://code.google.com/apis/console>.
        client_secrets = os.path.join(provider_path,
                                      'client_secrets.json')

        # Set up a Flow object to be used if we need to authenticate.
        flow = client.flow_from_clientsecrets(client_secrets,
                                              scope=scope,
                                              message=tools.message_if_missing(
                                                  client_secrets))

        # Prepare credentials, and authorize HTTP object with them.
        # If the credentials don't exist or are invalid run through the native
        # client flow. The Storage object will ensure that if successful the
        # good credentials will get written back to a file.
        storage = file.Storage(
            os.path.join(provider_path, name + '_credentials.dat'))
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow, storage, flags)
        http = credentials.authorize(http=build_http())

        # Construct a service object via the discovery service.
        self._service = discovery.build(name, version, http=http)

    def get_calendar(self, name):
        try:
            page_token = None
            while True:
                calendar_list = self._service.calendarList().list(
                    pageToken=page_token).execute()
                for calendar_list_entry in calendar_list['items']:
                    if calendar_list_entry['summary'] == name:
                        return calendar_list_entry['id']

                page_token = calendar_list.get('nextPageToken')
                if not page_token:
                    break

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize.')

        print('Calendar "%s" not found' % name)
        return None

    def read_entries(self, timesheet_id, start_date, end_date, parse):

        page_token = None
        while True:
            event_list = self._service.events().list(
                calendarId=timesheet_id,
                timeMin=start_date.isoformat() + "T00:00:00Z",
                timeMax=end_date.isoformat() + "T00:00:00Z",
                pageToken=page_token).execute()

            for entry in event_list['items']:
                def opt_arg(k):
                    try:
                        return entry[k]
                    except KeyError:
                        return ""

                if entry['status'] != 'confirmed':
                    print(
                        "WARNING: Ignoring entry  %s with status %s" %
                        (entry,
                         entry['status']), file=sys.stderr, end='\n')
                    continue

                text = entry["summary"]

                summary, key = parse(text)

                yield CalendarEntry(
                    entry["start"],
                    entry["end"],
                    summary,
                    opt_arg("description"),
                    opt_arg("location"),
                    entry["htmlLink"],
                    self._tz), key

            page_token = event_list.get('nextPageToken')
            if not page_token:
                break
