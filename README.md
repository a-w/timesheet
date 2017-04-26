Pretty print a timesheet, using the Google Calendar API

Author: (c) Adrian Weiler <timesheet-author.SPAM@aweiler.com>
Licensed under the Apache License. https://www.apache.org/licenses/LICENSE-2.0.html

Required python packages: see requirements.txt.

Required files (not included)

- client_secrets.json
- projects.sqlite
- user.json

How to get client secrets:
- follow instructions from https://support.google.com/googleapi/answer/6158841
and activate the Google Calendar API. You may need to create a project first.
- follow instructions from https://support.google.com/googleapi/answer/6158849?hl=en&ref_topic=7013279
and create an OAuth client id
- download JSON, save as client_secrets.json

How to create/edit the project database:
- execute projects.sql with sqlite3 or https://addons.mozilla.org/de/firefox/addon/sqlite-manager/

What is in user.json?
```json
{
  "user": "your_initials",
  "title" : "What you want to see as title in the report"
}
```

On the first call, the application will open your browser to request your consent for accessing your calendar.
This consent can be revoked at any time in visiting https://myaccount.google.com/permissions.
Result is cached in a file named calendar_credentials.dat

The application will process the calendar named by the `--calendar` command line parameter, which defaults to `Log`.
By default, the last month (i.e. the full month before the current one) will be processed.
A different time span can be specified with `--start-date` and `--end-date`. The latter defaults to end of today.

The application will assume that all calendar entries in the given calendar look like

```
[KEY]Text
```

Where `KEY` is a project key of a project defined in `projects.sqlite`.
If such a project cannot be found, your browser is headed at the calendar entry to allow you to fix the entry.


KUDOS:
Some code is from the Google samples. Licensed and redistributed under the Apache License.
The XSLT sample and the embedded CSS were originally written by Sören Sprößig.

DISCLAIMER:
No warranty whatsoever. Use at your own risk.
Some keywords in the sample XSLT are in German. Feel free to translate.
