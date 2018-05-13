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

import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"

DATE_TIME_RE = re.compile(
    '(?P<Y>\\d\\d\\d\\d)-'
    '(?P<m>1[0-2]|0[1-9]|[1-9])-'
    '(?P<d>3[0-1]|[1-2]\\d|0[1-9])T'
    '(?P<H>2[0-3]|[0-1]\\d|\\d):'
    '(?P<M>[0-5]\\d|\\d):'
    '(?P<S>6[0-1]|[0-5]\\d|\\d)'
    '(?P<zh>[+-]\\d\\d):'
    '(?P<zm>[0-5]\\d)')

DATE_RE = re.compile(
    '(?P<Y>\\d\\d\\d\\d)-'
    '(?P<m>1[0-2]|0[1-9]|[1-9])-'
    '(?P<d>3[0-1]|[1-2]\\d|0[1-9])')


class CalendarEntry:
    # pylint: disable=too-few-public-methods

    def __init__(self, start, end, summary, description, location,
                 link, default_tz):
        # pylint: disable=too-many-arguments

        def to_datetime(entry):
            try:
                inp = entry["dateTime"]
                found = DATE_TIME_RE.fullmatch(inp)
            except KeyError:
                inp = entry["date"]
                found = DATE_RE.fullmatch(inp)

            if not found:
                raise ValueError("time data %r does not match expected format"
                                 % inp)

            _ = defaultdict(int)
            _.update(found.groupdict())

            if isinstance(_["zh"], int):
                return default_tz.localize(
                    datetime(int(_["Y"]), int(_["m"]), int(_["d"]),
                             int(_["H"]), int(_["M"])))

            return datetime(int(_["Y"]), int(_["m"]), int(_["d"]),
                            int(_["H"]), int(_["M"]), tzinfo=timezone(
                    timedelta(hours=int(_["zh"]), minutes=int(_["zm"]))))

        self.start = to_datetime(start)
        self.end = to_datetime(end)
        self.summary = summary
        self.description = description
        self.location = location
        self.link = link
