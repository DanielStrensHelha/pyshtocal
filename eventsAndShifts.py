import datetime

"""------------------------------------- FUNCTIONS -------------------------------------"""
def checkShiftEvent(event, shiftList):
    """
    Will check if a work event is in the list of events.
    If it isn't, it must be deleted from the agenda. 
    If it is, it must be deleted from the list of events to add (shiftList)
    Returns -1 if the event shouldn't exist
    Return the position of the event in the list otherwise.
    """
    found = False
    eventDateTemp = event['start']['dateTime']
    eventDate = datetime.date(int(eventDateTemp[0:4]), int(eventDateTemp[5:7]), int(eventDateTemp[8:10]))
    
    eventStartTime = datetime.time(int(eventDateTemp[11:13]), int(eventDateTemp[14:16]), 0)

    eventDateTemp = event['end']['dateTime']
    eventEndTime = datetime.time(int(eventDateTemp[11:13]), int(eventDateTemp[14:16]), 0)

    print("\nEvent date = ", eventDate, '\nStarts at', eventStartTime, 'and ends at', eventEndTime)

    for i, (date, start, end) in enumerate(shiftList):
        shiftStart = datetime.time(int(start[0:2]), int(start[3:5]), 0)
        shiftEnd = datetime.time(int(end[0:2]), int(end[3:5]), 0)
        
        if (eventDate.strftime("%d/%m/%Y") == date):
            if shiftStart == eventStartTime and shiftEnd == eventEndTime:
                print('Event to keep ✅')
                return i

    print("Event to delete ❌")
    return -1


def dateTimeFromShift(date, time, season):
    toReturn = str(date[6:10] + '-' + date[3:5] + '-' + date[0:2] + 'T' + time[0:2] + ':' + time[3:5])

    toReturn += ':00+01:00' if season == "winter" else ':00+02:00'
    
    return toReturn