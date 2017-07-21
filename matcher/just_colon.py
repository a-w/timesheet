# -*- coding: utf-8 -*-
# Copyright 2017 Adrian Weiler. All Rights Reserved.
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

"""Matcher for a simplified layout project:text."""

from ._regex_common import RegexMatcher

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"

MATCHER = RegexMatcher('(?P<key>[a-z0-9 _-]*):(?P<description>.*)')


def match(text):
    """
    Parse calendar entry
    :param text: The entry to parse
    :return: A pair of description, project key
    """
    return MATCHER.match(text)
