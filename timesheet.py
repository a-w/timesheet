#!/usr/bin/env python
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

"""Time sheet evaluator that uses the Google Calendar API."""

import json
import os.path
import re
import sqlite3
import subprocess
import sys
import tempfile
import webbrowser
from collections import defaultdict
from datetime import datetime, date, timedelta

import humanfriendly
from lxml import etree
from oauth2client import client

import matcher
from helpers import init

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"

DATE_TIME_RE = re.compile(
    '(?P<Y>\\d\\d\\d\\d)-'
    '(?P<m>1[0-2]|0[1-9]|[1-9])-'
    '(?P<d>3[0-1]|[1-2]\\d|0[1-9])T'
    '(?P<H>2[0-3]|[0-1]\\d|\\d):'
    '(?P<M>[0-5]\\d|\\d):'
    '(?P<S>6[0-1]|[0-5]\\d|\\d)'
    '(?P<z>[+-]\\d\\d:[0-5]\\d)')

DATE_RE = re.compile(
    '(?P<Y>\\d\\d\\d\\d)-'
    '(?P<m>1[0-2]|0[1-9]|[1-9])-'
    '(?P<d>3[0-1]|[1-2]\\d|0[1-9])')

DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"


def _print_msg(entry, msg):
    print("%s in entry at %s" % (msg, entry["start"]), end='\n')


def _open_browser(entry, msg):
    _print_msg(entry, msg)
    webbrowser.open(entry["htmlLink"], new=2)


class CalendarEntry:
    # pylint: disable=too-few-public-methods

    def __init__(self, entry_id, start, end, summary, description, location,
                 link):
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

            _ = defaultdict(int, found.groupdict())
            return datetime(int(_["Y"]), int(_["m"]), int(_["d"]),
                            int(_["H"]), int(_["M"]))

        self.entry_id = entry_id
        self.start = to_datetime(start)
        self.end = to_datetime(end)
        self.summary = summary
        self.description = description
        self.location = location
        self.link = link


class Project:
    # pylint: disable=too-few-public-methods

    def __init__(self, pid, key, title):
        self.pid = pid
        self.key = key
        self.title = title
        self.kvp = dict()


class UsedProject:
    # pylint: disable=too-few-public-methods

    def __init__(self, project):
        self.project = project
        self.entries = []


class CalendarDb:
    # pylint: disable=too-few-public-methods

    def __init__(self, name):
        self.conn = sqlite3.connect(name)

    def get_projects(self):
        cursor = self.conn.cursor()
        project = None
        # noinspection SqlResolve
        projects = cursor.execute("SELECT p.Id, p.ProjectKey, p.ProjectTitle, "
                             "kvp.Key, kvp.value "
                             "FROM Projects p "
                             "LEFT JOIN ProjectKeyValuePairs kvp "
                             "ON p.Id = kvp.ProjectID "
                             "ORDER BY p.ProjectKey")
        for pid, project_key, title, kvk, kvv in projects:
            if project is None or project.pid != pid:
                if project is not None:
                    yield project
                project = Project(pid, project_key, title)
            if kvk is not None:
                project.kvp[kvk] = kvv
        if project is not None:
            yield project


class TimeSheet:
    def __init__(self, argv):
        # Authenticate and construct service.
        self.service, self.arguments = init(
            argv, 'calendar', 'v3', __doc__, __file__,
            parents=[self._create_argument_parser()],
            scope='https://www.googleapis.com/auth/calendar.readonly')

        # user info
        with open("user.json", 'r', encoding='utf-8') as _:
            self.user_data = json.load(_)

        # projects database
        self.database = CalendarDb(self.arguments.database)
        self.projects = dict()
        for project in self.database.get_projects():
            self.projects[project.key] = project

        # start and end date
        if self.arguments.start_date is None and \
                self.arguments.end_date is None and \
                self.arguments.period is None:
            self.arguments.period = "last-month"

        self.start_date = date.today().replace(day=1)
        self.end_date = date.today() + timedelta(days=1)

        if self.arguments.period is not None:
            if self.arguments.period == "last-month":
                self.end_date = self.start_date
                self.start_date = (self.end_date - timedelta(days=1)).replace(
                    day=1)
            elif self.arguments.period == "current-month":
                pass
            else:
                raise ValueError("Unknown period: %s" % self.arguments.period)
            if self.arguments.start_date is not None or \
                    self.arguments.end_date is not None:
                raise ValueError(
                    "You cannot combine --period and explicit date")
        else:
            if self.arguments.start_date is not None:
                # pylint: disable=unused-variable
                year, month, day, *_ = humanfriendly.parse_date(
                    self.arguments.start_date)
                self.start_date = date(year, month, day)

            if self.arguments.end_date is not None:
                year, month, day, *_ = humanfriendly.parse_date(
                    self.arguments.end_date)
                self.end_date = date(year, month, day)

    def get_calendar(self, name):
        try:
            page_token = None
            while True:
                calendar_list = self.service.calendarList().list(
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

    def read_entries(self, timesheet_id):

        page_token = None
        while True:
            event_list = self.service.events().list(
                calendarId=timesheet_id,
                timeMin=self.start_date.isoformat() + "T00:00:00Z",
                timeMax=self.end_date.isoformat() + "T00:00:00Z",
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
                for match in matcher.MATCHERS:
                    summary, key = match(text)
                    if key is not None:
                        break

                yield CalendarEntry(entry["iCalUID"],
                                    entry["start"],
                                    entry["end"],
                                    summary,
                                    opt_arg("description"),
                                    opt_arg("location"),
                                    entry["htmlLink"]), key, entry

            page_token = event_list.get('nextPageToken')
            if not page_token:
                break

    @staticmethod
    def _create_argument_parser():
        import argparse

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--start-date',
                            help='Start date for evaluating calendar entries.')
        parser.add_argument('--end-date',
                            help='End date for evaluating calendar entries.')
        parser.add_argument('--period',
                            help='Shortcut for start and end dates.')
        parser.add_argument('--calendar', default='Log',
                            help='The name of the calendar to search.')
        parser.add_argument('--database', default='projects.sqlite',
                            help='The project database.')
        parser.add_argument('--link', action='store_true',
                            help='Make description a hyperlink.')
        parser.add_argument('--link-error', action='store_true',
                            help="Make errors a hyperlink, don't open entry.")
        parser.add_argument('--project', action='append',
                            help="Select a specific project. This option may "
                                 "be specified multiple times.")
        parser.add_argument('--xslt', default='CreateReport.xslt',
                            help='The style sheet to use.')
        return parser

    def export_as_xml(self, used_projects):
        root = etree.Element("timesheet")
        projects = etree.SubElement(root, "projects")
        entries = etree.SubElement(root, "entries")
        etree.SubElement(root, "summary",
                         title=self.user_data["title"],
                         start=self.start_date.strftime(DATE_FORMAT),
                         end=(self.end_date - timedelta(days=1))
                         .strftime(DATE_FORMAT))

        for project_key in sorted(used_projects):
            used_project = used_projects[project_key]
            project_element = etree.SubElement(projects, "project",
                                  title=used_project.project.title,
                                  key=project_key)
            if used_project.project.kvp:
                props = etree.SubElement(project_element, "properties")
                for key, value in used_project.project.kvp.items():
                    etree.SubElement(props, "p", key=key, value=value)

            # pylint: disable=invalid-name
            for e in sorted(used_project.entries, key=lambda x: x.start):
                entry = etree.SubElement(
                    entries, "entry", key=project_key,
                    attrib={"from": e.start.strftime(TIME_FORMAT),
                            "to": e.end.strftime(TIME_FORMAT),
                            "minutes": str(((e.end - e.start) / 60).seconds),
                            "subject": e.summary.strip()})
                if self.arguments.link \
                    or self.arguments.link_error \
                        and used_project.project.pid == 0:
                    entry.attrib["link"] = e.link
                if e.description:
                    etree.SubElement(entry, "details").text = \
                        e.description.strip()

        # print(etree.tostring(root, encoding="unicode", pretty_print=True))
        return root

    def read_calendar(self, timesheet_id, error_callback):
        used_projects = dict()
        for calendar_entry, key, entry in self.read_entries(timesheet_id):
            project = None

            if key is None:
                error_callback(entry,
                               "Malformed timesheet entry: %s" %
                               entry['summary'])
                key = "unknown"
            else:
                try:
                    project = self.projects[key]
                except KeyError:
                    error_callback(entry, "Unknown project: %s" % key)

            if self.arguments.project is not None:
                if key not in self.arguments.project:
                    continue

            try:
                used_project = used_projects[key]
            except KeyError:
                if project is None:
                    project = Project(0, key, "Unknown project")
                used_project = UsedProject(project)
                used_projects[key] = used_project

            used_project.entries.append(calendar_entry)
        return used_projects

    @staticmethod
    def transform_to_html(xslt_file, xml, file_name):
        temp_path = os.path.join(tempfile.gettempdir(), file_name)
        html_filename = temp_path + ".html"

        xsltproc = where("xsltproc")

        if xsltproc is not None:
            try:
                xml_filename = temp_path + ".xml"
                with open(xml_filename, "w", encoding="utf-8") as xml_file:
                    xml_file.write(
                        etree.tostring(xml, encoding="unicode"))
                subprocess.check_call([xsltproc, "-o", html_filename,
                                       xslt_file,
                                       xml_filename])
                return html_filename
            except subprocess.CalledProcessError:
                print("An error occurred while calling \"%s\". "
                      "See output above." % xsltproc)

        transformed = etree.XSLT(etree.parse(xslt_file))(xml)
        with open(html_filename, "w", encoding="utf-8") as output_file:
            output_file.write(
                etree.tostring(transformed, encoding="unicode",
                               pretty_print=True))
        return html_filename

    def main(self):
        calendar_id = self.get_calendar(self.arguments.calendar)
        if calendar_id is not None:
            error_cb = _print_msg if self.arguments.link \
                                     or self.arguments.link_error \
                                     else _open_browser
            xml = self.export_as_xml(
                self.read_calendar(calendar_id, error_cb))

            html_file = TimeSheet.transform_to_html(
                self.arguments.xslt, xml, "atb_%s_%s" % (
                    self.user_data["user"],
                    datetime.now().strftime("%Y%d%m_%H%M")))
            webbrowser.open(html_file, new=2)

        return 0


def where(file_name):
    import platform
    # inspired by http://nedbatchelder.com/code/utilities/wh.py
    # see also: http://stackoverflow.com/questions/11210104/
    path_sep = ":" if platform.system() == "Linux" else ";"
    path_ext = [''] if platform.system() == "Linux" or '.' in file_name \
        else os.environ["PATHEXT"].split(path_sep)
    for d in os.environ["PATH"].split(path_sep):
        for e in path_ext:
            file_path = os.path.join(d, file_name + e)
            if os.path.exists(file_path):
                return file_path
    return None


if __name__ == '__main__':
    sys.exit(TimeSheet(sys.argv).main())
