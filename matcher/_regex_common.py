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

"""Common code for matchers using regular expressions."""

import re

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"


class RegexMatcher:
    """A Matcher that uses a regular expression"""

    # pylint: disable=too-few-public-methods
    def __init__(self, expression):
        """
        Constructor
        :param expression:The regular expression to use.
        The expression MUST have
           * a group named "key" and
           * a group named "description"
        """
        self.regex = re.compile(expression, re.IGNORECASE)

    def match(self, text):
        """
        Match the given text against the regular expression
        :param text: The calendar entry to parse
        :return: A pair of description, project key
        """
        parsed = self.regex.fullmatch(text)
        if parsed is None:
            return text, None
        group_dict = parsed.groupdict()
        return group_dict["description"], group_dict["key"]
