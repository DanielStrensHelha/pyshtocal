# to install google packages
# py -m venv env
# .\env\Scripts\activate
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# 

from __future__ import print_function

import datetime
import os.path
from eventsAndShifts import *
from personnal.informations import SPREADSHEAT_ID, RANGE_NAME, CALENDAR_ID, TIME_ZONE

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2 import service_account

# This part is related to the authorizations needed by the script
SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/spreadsheets']

creds = None;
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


"""---------------------------------------- MAIN FUNCTION ----------------------------------------"""
def main():
    """ Fetches date and time of work in sheet, then creates / updates events in google calendar. """
    success = False

    # Fetching data from google sheets
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEAT_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        
        success = True

    except HttpError as err:
        print(err)

    # creates / updates events in calendar
    if success:
        shiftList = values

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the calendar api
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('\n\nGetting the events... ')
            events_result = service.events().list(calendarId=CALENDAR_ID, timeMin="2022-08-01T08:00:00Z",
                                                maxResults=2500, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No events found.')

            # Purge calendar and list of events to add :
            season = "summer"
            

            for event in events:
                if (event['summary'] == 'Time change'):
                    print("\n\nEVENT TIME CHANGE DETECTED :\n" + season + "\nTO ")
                    print(event["description"])

                    eventDateTemp = event['start']['dateTime']
                    eventDate = datetime.date(int(eventDateTemp[0:4]), int(eventDateTemp[5:7]), int(eventDateTemp[8:10]))
                    
                    for i, shift in enumerate(shiftList):
                        if (eventDate.strftime("%d/%m/%Y") == shift[0]):
                            for j in range(i):
                                del shiftList[0]
                            
                            break

                        print('shift to add : ', shift)
                        addShift(shift, season, service)

                    
                    season = event["description"]
                    continue

                pos = checkShiftEvent(event, shiftList)
                
                if pos >= 0:
                    del shiftList[pos]
                else:
                    print("deleting event; id =", event['id'], "Date and time : ", event['start'])
                    service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
            
            # Add events to calendar            
            for i, shift in enumerate(shiftList):
                print('shift to add : ', shift)
                addShift(shift, season, service)

        except HttpError as error:
            print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
    exit()