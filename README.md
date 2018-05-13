# Time sheet pretty printer

A time sheet consists of specially formatted calendar entries.

The time sheet pretty printer supports

- the Google Calendar API
- CalDAV, tested with [Nextcloud](https://nextcloud.com)

Author: (c) Adrian Weiler <timesheet-author.SPAM@aweiler.com>
Licensed under the Apache License. https://www.apache.org/licenses/LICENSE-2.0.html

Required python packages: see requirements.txt.

Required files (not included)

- client_secrets.json
- projects.sqlite
- user.json
- calendar.json (for CalDAV only, supplied for Google Calendar)

How to get client secrets:

see provider specific instructions at

- [provider/google/README.md](provider/google/README.md)
- [provider/caldav/README.md](provider/caldav/README.md)

How to create/edit the project database:

- execute projects.sql with sqlite3

What is in user.json?

```json
{
  "user": "your_initials",
  "title": "What you want to see as title in the report",
  "tz": "your timezone, e.g. 'Europe/Berlin'"
}
```

The application will process the calendar named by the `--calendar` command line parameter, which defaults to `Log`.
By default, the last month (i.e. the full month before the current one) will be processed.
A different time span can be specified with `--start-date` and `--end-date`, where `start-date <= matching date < end-data` (`end-date` is non-inclusive). The latter defaults to end of today.

The application will assume that all calendar entries in the given calendar look either like

```none
[KEY]Text
```

or like

```none
KEY:Text
```

Where `KEY` is a project key of a project defined in `projects.sqlite`.
If such a project cannot be found, your browser is headed at the calendar entry to allow you to fix the entry.

KUDOS:
Some code is from the Google samples. Licensed and redistributed under the Apache License.
The XSLT sample and the embedded CSS were originally written by Sören Sprößig.

DISCLAIMER:
No warranty whatsoever. Use at your own risk.
Some keywords in the sample XSLT are in German. Feel free to translate.
