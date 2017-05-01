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

from datetime import datetime, date, timedelta
import humanfriendly
import json
import os.path
import re
import sqlite3
import sys
import tempfile
import webbrowser
from lxml import etree

from oauth2client import client
from helpers import init

__author__ = "Adrian Weiler <timesheet-author.SPAM@aweiler.com>"

date_time_re = re.compile(
    '(?P<Y>\\d\\d\\d\\d)-'
    '(?P<m>1[0-2]|0[1-9]|[1-9])-'
    '(?P<d>3[0-1]|[1-2]\\d|0[1-9])T'
    '(?P<H>2[0-3]|[0-1]\\d|\\d):'
    '(?P<M>[0-5]\\d|\\d):'
    '(?P<S>6[0-1]|[0-5]\\d|\\d)'
    '(?P<z>[+-]\\d\\d:[0-5]\\d)')

entry_re = re.compile('\[(?P<p>[a-z0-9 _-]*)\](?P<d>.*)',
                      re.IGNORECASE)

DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"


def _open_browser(e, msg):
    print(msg, end='\n')
    webbrowser.open(e["htmlLink"], new=2)


class CalendarEntry:
    def __init__(self, entry_id, start, end, summary, description, location,
                 link):
        def to_datetime(s):
            global date_time_re
            inp = s["dateTime"]
            found = date_time_re.fullmatch(inp)
            if not found:
                raise ValueError("time data %r does not match expected format"
                                 % inp)

            d = found.groupdict()
            return datetime(int(d["Y"]), int(d["m"]), int(d["d"]),
                            int(d["H"]), int(d["M"]))

        self.id = entry_id
        self.start = to_datetime(start)
        self.end = to_datetime(end)
        self.summary = summary
        self.description = description
        self.location = location
        self.link = link


class Project:
    def __init__(self, pid, key, title):
        self.pid = pid
        self.key = key
        self.title = title
        self.kvp = dict()


class UsedProject:
    def __init__(self, project):
        self.project = project
        self.entries = []


class CalendarDb:
    def __init__(self, name):
        self.conn = sqlite3.connect(name)

    def get_projects(self):
        c = self.conn.cursor()
        p = None
        # noinspection SqlResolve
        projects = c.execute("SELECT p.Id, p.ProjectKey, p.ProjectTitle, "
                             "kvp.Key, kvp.value "
                             "FROM Projects p "
                             "LEFT JOIN ProjectKeyValuePairs kvp "
                             "ON p.Id = kvp.ProjectID "
                             "ORDER BY p.ProjectKey")
        for pid, project_key, title, kvk, kvv in projects:
            if p is None or p.pid != pid:
                if p is not None:
                    yield p
                p = Project(pid, project_key, title)
            if kvk is not None:
                p.kvp[kvk] = kvv
        if p is not None:
            yield p


class TimeSheet:
    def __init__(self, argv):
        # Authenticate and construct service.
        self.service, self.arguments = init(
            argv, 'calendar', 'v3', __doc__, __file__,
            parents=[self._create_argument_parser()],
            scope='https://www.googleapis.com/auth/calendar.readonly')

        # user info
        self.user = None
        self.title = None
        with open("user.json", 'r') as fp:
            user_data = json.load(fp)
            self.user = user_data["user"]
            self.title = user_data["title"]

        # projects database
        self.db = CalendarDb(self.arguments.database)
        self.projects = dict()
        for p in self.db.get_projects():
            self.projects[p.key] = p

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
            else:
                raise ValueError("Unknown period: %s" % self.arguments.period)
            if self.arguments.start_date is not None or \
                    self.arguments.end_date is not None:
                raise ValueError(
                    "You cannot combine --period and explicit date")
        else:
            if self.arguments.start_date is not None:
                y, m, d, *r = humanfriendly.parse_date(
                    self.arguments.start_date)
                self.start_date = date(y, m, d)
            if self.arguments.end_date is not None:
                y, m, d, *r = humanfriendly.parse_date(
                    self.arguments.end_date)
                self.end_date = date(y, m, d)

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
                    continue

                project = entry_re.fullmatch(entry["summary"])
                if project is None:
                    summary = entry["summary"]
                    key = None
                else:
                    d = project.groupdict()
                    summary = d["d"]
                    key = d["p"]

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
        parser.add_argument('--xslt', default='CreateReport.xslt',
                            help='The style sheet to use.')
        return parser

    def export_as_xml(self, used_projects):
        root = etree.Element("timesheet")
        projects = etree.SubElement(root, "projects")
        entries = etree.SubElement(root, "entries")
        etree.SubElement(root, "summary",
                         title=self.title,
                         start=self.start_date.strftime(DATE_FORMAT),
                         end=(self.end_date - timedelta(days=1))
                         .strftime(DATE_FORMAT))

        for used_project in sorted(used_projects):
            p = used_projects[used_project]
            xp = etree.SubElement(projects, "project",
                                  title=p.project.title,
                                  key=used_project)
            if len(p.project.kvp) > 0:
                props = etree.SubElement(xp, "properties")
                for k, v in p.project.kvp.items():
                    etree.SubElement(props, "p", key=k, value=v)

            for e in sorted(p.entries, key=lambda x: x.start):
                entry = etree.SubElement(
                    entries, "entry", key=used_project,
                    attrib={"from": e.start.strftime(TIME_FORMAT),
                            "to": e.end.strftime(TIME_FORMAT),
                            "minutes": str((e.end - e.start).seconds // 60),
                            "subject": e.summary})
                if self.arguments.link:
                    entry.attrib["link"] = e.link
                if len(e.description) > 0:
                    etree.SubElement(entry, "details").text = e.description

        # print(etree.tostring(root, encoding="unicode", pretty_print=True))
        return root

    def read_calendar(self, timesheet_id, error_callback):
        used_projects = dict()
        for e, key, entry in self.read_entries(timesheet_id):
            project = None

            if key is None:
                error_callback(entry,
                               "Malformed timesheet entry: %s" %
                               entry.summary)
                key = "unknown"
            else:
                try:
                    project = self.projects[key]
                except KeyError:
                    error_callback(entry, "Unknown project: %s" % key)

            try:
                used_project = used_projects[key]
            except KeyError:
                if project is None:
                    project = Project(0, key, "Unknown project")
                used_project = UsedProject(project)
                used_projects[key] = used_project

            used_project.entries.append(e)
        return used_projects

    @staticmethod
    def transform_to_html(xslt_file, xml, file_name):
        transformed = etree.XSLT(etree.parse(xslt_file))(xml)
        t = os.path.join(tempfile.gettempdir(), file_name)
        with open(t, "w", encoding="utf-8") as f:
            f.write(
                etree.tostring(transformed, encoding="unicode",
                               pretty_print=True))
        return t

    def main(self):
        calendar_id = self.get_calendar(self.arguments.calendar)
        if calendar_id is not None:
            xml = self.export_as_xml(
                self.read_calendar(calendar_id, _open_browser))

            html_file = TimeSheet.transform_to_html(
                self.arguments.xslt, xml, "atb_%s_%s.html" % (
                    self.user, datetime.now().strftime("%Y%d%m_%H%M")))
            webbrowser.open(html_file, new=2)

        return 0


if __name__ == '__main__':
    sys.exit(TimeSheet(sys.argv).main())
