# Google calendar specific instructions

## How to get client credentials

- follow instructions from https://support.google.com/googleapi/answer/6158841 and activate the Google Calendar API. You may need to create a project first.
- follow instructions from https://support.google.com/googleapi/answer/6158849?hl=en&ref_topic=7013279 and create an OAuth client id
- download JSON, save as client_secrets.json

On the first call, the application will open your browser to request your consent for accessing your calendar.
This consent can be revoked at any time in visiting https://myaccount.google.com/permissions.
Result is cached in a file named calendar_credentials.dat
