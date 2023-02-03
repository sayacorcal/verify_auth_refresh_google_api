import csv
import time
import datetime
import json
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES        = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/spreadsheets.readonly"]
token_file    = "token.json"
CLIENT_SECRET = "credentials.json"
creds = None

test_refresh_token_sheet_id   = "1yI5KLon6HCOQemwDlDoJb1pqJqSpVEahnpgrTY86ulo"
test_refresh_token_range_name = "test_refresh_token"

def refresh_creds(row_value):
    # Write the expiration time and the current time to a CSV file.
    with open('token_expiration.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row_value)

# function to add new row to some sheet
def add_new_row(creds=None, sheet_id=None, range_name=None, row_value=None):
  try:
    service = build('sheets', 'v4', credentials=creds)
    values = [row_value]
    body = {'values': values}
    result = service.spreadsheets()
    result = result.values().append( spreadsheetId=sheet_id, 
                                    range=range_name,
                                    valueInputOption="USER_ENTERED", 
                                    body=body).execute()
    print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
    return True
  except HttpError as error:
    print(f"An error occurred: {error}")
    return False

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

# Check every minute if the credentials have expired.
while True:
    # If there are no (valid) credentials available or if the token is expired, refresh it.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
    #get the actual date on day/month/year hour/minute/second format
    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    row_value = [str(creds.expiry),str(current_time)]
    # save actual value as token_expiration.csv file
    refresh_creds(row_value)
    print("row_value_dumps: ",row_value)
    # save actual value in a google sheet file 
    add_new_row(creds=creds, sheet_id=test_refresh_token_sheet_id, range_name=test_refresh_token_range_name, row_value=row_value)

    # read a break.json file that will break the loop if its false
    with open("break.json", "r") as f:
       data = json.load(f)
    if not("key" in data) or data["key"] == False:
        break
    time.sleep(60) # wait for a minute before checking again
    