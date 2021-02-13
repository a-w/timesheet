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

"""Timeular API interface for the time sheet evaluator."""

from datetime import datetime, timezone

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


def _convert_time(date_time, tz):
    dt = datetime.fromisoformat(date_time)
    ts = dt.replace(tzinfo=timezone.utc).timestamp()
    ts = (ts + 450) // 900 * 900
    dt = datetime.fromtimestamp(ts, tz)
    return dt


class CalendarEntry:
    """
    Represents a single calendar entry
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, entry, activity, default_tz):
        duration = entry['duration']
        note = entry['note']
        self.start = _convert_time(duration['startedAt'], default_tz)
        self.end = _convert_time(duration['stoppedAt'], default_tz)
        text = note.get('text')
        self.summary = activity[0] if text is None else text
        self.description = ''
