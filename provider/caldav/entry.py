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

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


class CalendarEntry:
    # pylint: disable=too-few-public-methods

    def __init__(self, start, end, summary, description, location,
                 link, default_tz):
        # pylint: disable=too-many-arguments
        def to_datetime(entry):
            if isinstance(entry, datetime):
                return entry

            return default_tz.localize(
                datetime.combine(entry, time())).astimezone(
                timezone.utc)

        self.start = to_datetime(start)
        self.end = to_datetime(end)
        self.summary = summary
        self.description = description
        self.location = location
        self.link = link
