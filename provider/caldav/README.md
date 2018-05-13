# CalDAV/Nextcloud specific instructions

The time sheet pretty printer supports access via OAuth2 only.
This has been tested only with Nextcloud and thus the following instructions apply to nextcloud.

## Create calendar.json

You must first create `calendar.json` in order to tell the program how to access your calendar. It should look like this:

```json
{
  "name": "mycalendarname",
  "url": "https://mycloud.example.com/remote.php/dav/"
}
```

You may use any `name`. It will be used as part of the JSON files below.

## How to get client credentials

In Nextcloud, go to the [security settings](https://mycloud.example.com/settings/admin/security). There is a section OAuth 2.0 clients. Add a client. You can use any name, e.g. `calendar`, but it is important that the redirect URI is http://localhost:8080. Click "add". You should now see a new client ID. Copy the client ID and the secret (click the eye icon to reveal) to `mycalendarname_secrets.json` in the `provider/caldav` folder which should then look like this:

```json
{
  "web": {
    "client_id": "stuff copied from Client Identifier",
    "client_secret": "stuff copied from secret",
    "auth_uri": "https://mycloud.example.com/index.php/apps/oauth2/authorize",
    "token_uri": "https://mycloud.example.com/index.php/apps/oauth2/api/v1/token",
    "redirect_uris": []
  }
}
```

On the first call, the application will open your browser to request your consent for accessing your calendar. There should be a message saying "You are about to grant **calendar** access to your mycloud.example.com account." Click "Grant access". After entering your username and password, the browser should now be redirected to http://localhost:8080 and you should see the message "The authentication flow has completed."

The credentials will be saved to `mycalendarname_credentials.dat`.
