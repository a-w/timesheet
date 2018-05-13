# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Utilities for making samples.

Consolidates a lot of code commonly repeated in sample applications.
"""

import argparse
from importlib import import_module
import json
import os

from oauth2client import tools

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__author__ += 'Adrian Weiler <timesheet-author.SPAM@aweiler.com>'


def init(argv, tz, doc, parents=()):
    """A common initialization routine for samples.

  Many of the sample applications do the same initialization, which has now
  been consolidated into this function. This function uses common idioms found
  in almost all the samples, i.e. for an API with name 'apiname', the
  credentials are stored in a file named apiname.dat, and the
  client_secrets.json file is stored in the same directory as the application
  main file.

  Args:
    argv: list of string, the command-line parameters of the application.
    tz: default timezone to use
    doc: string, description of the application. Usually set to __doc__.
    parents: list of argparse.ArgumentParser, additional command-line flags.

  Returns:
    A tuple of (service, flags), where service is the service object and flags
    is the parsed command-line flags.
  """

    # Parser command-line arguments.
    def _provider_parser():
        _ = argparse.ArgumentParser(add_help=False)
        _.add_argument('--provider', default='google',
                       help='The calendar provider to use.')
        return _

    parent_parsers = [tools.argparser, _provider_parser()]
    parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
        description=doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parent_parsers)
    flags = parser.parse_args(argv[1:])

    provider_config = os.path.join(os.path.dirname(__file__),
                                   'provider',
                                   flags.provider,
                                   'calendar.json')

    with open(provider_config, 'r', encoding='utf-8') as _:
        config = json.load(_)

    # Pass timezone info from user config
    config["tz"] = tz

    return import_module(
        'provider.' + flags.provider).Provider(config, flags), flags
