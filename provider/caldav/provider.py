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

"""CalDAV API interface for the time sheet evaluator."""

from datetime import datetime, time, timezone
import os
from caldav import DAVClient
from icalendar import Calendar
from oauth2client import client, file, tools
from .oauth import OAuth
from .entry import CalendarEntry

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


class Provider(object):
    def __init__(self, config, flags):
        name = config.get("name", "calendar")
        url = config.get("url")
        self._tz = config.get("tz", "utc")

        provider_path = os.path.dirname(__file__)
        client_secrets = os.path.join(provider_path,
                                      name + '_secrets.json')

        flow = client.flow_from_clientsecrets(client_secrets,
                                              scope="",
                                              message=tools.message_if_missing(
                                                  client_secrets))

        storage = file.Storage(
            os.path.join(provider_path, name + '_credentials.dat'))
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow, storage, flags)

        self._client = DAVClient(url, auth=OAuth(credentials))

    def get_calendar(self, name):
        principal = self._client.principal()
        calendars = principal.calendars()

        match = name.casefold()

        for calendar in iter(calendars):
            pfx, local_name, _ = calendar.canonical_url.rsplit("/", 2)

            if local_name.casefold() == match:
                return calendar

        return None

    def read_entries(self, calendar, start_date, end_date, parse):
        midnight = time()
        start = self._tz.localize(
            datetime.combine(start_date, midnight)).astimezone(timezone.utc)
        end = self._tz.localize(
            datetime.combine(end_date, midnight)).astimezone(timezone.utc)
        results = calendar.date_search(start, end)

        for event in results:
            cal = Calendar.from_ical(event.data)
            for ev in cal.subcomponents:
                if ev.name == "VEVENT":
                    text = ev.get('summary')
                    summary, key = parse(text)

                    yield CalendarEntry(
                        ev.get('dtstart').dt,
                        ev.get('dtend').dt,
                        summary,
                        ev.get('description'),
                        ev.get('location'),
                        event.canonical_url,
                        self._tz), key
