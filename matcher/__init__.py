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

"""Package initialization for dynamically loadable matcher modules."""

import glob
from os.path import basename, dirname, isfile
from importlib import import_module

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"

# kudos https://stackoverflow.com/a/1057534/2311167
_MODULES = glob.glob(dirname(__file__) + "/*.py")

__all__ = [basename(f)[:-3] for f in _MODULES if
           isfile(f)
           and not f.endswith("__init__.py")
           and not f.endswith("_common.py")]

MATCHERS = [import_module('.' + x, 'matcher').__dict__['match']
            for x in __all__]
