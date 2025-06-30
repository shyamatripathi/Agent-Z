
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

SCOPES = []

def authenticate_google_calendar():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # Save as JSON
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    print(" Token saved in token.json!")

if __name__ == '__main__':
    authenticate_google_calendar()
