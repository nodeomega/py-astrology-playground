from datetime import datetime, timedelta

import pytz

bodyPriority = {
  "Sun": 0, 
  "Moon": 1, 
  "Mercury": 2, 
  "Venus": 3, 
  "Mars": 4, 
  "Jupiter": 5, 
  "Saturn": 6, 
  "Uranus": 7, 
  "Neptune": 8, 
  "Pluto": 9, 
  "Chiron": 10, 
  "Ceres": 11,
  "Juno": 12,
  "Pallas": 13,
  "Vesta": 14,
  "True Node": 15, 
  "Black Moon Lilith": 16
  }

def ShouldFlipBodies(body1Name, body2Name):
  """Sorting function, used for sorting astrological bodies in preferred order."""
  if (bodyPriority.get(body1Name) == None and bodyPriority.get(body2Name) == None):
    if (body1Name.lower() < body2Name.lower()):
      return False
    else:
      return True
  elif (bodyPriority.get(body1Name) != None and bodyPriority.get(body2Name) == None):
    return False
  elif (bodyPriority.get(body1Name) == None and bodyPriority.get(body2Name) != None):
    return True
  else:
    if (bodyPriority.get(body1Name) < bodyPriority.get(body2Name)):
      return False
    else:
      return True
    
def FormatDateTimeString(dt: datetime):
  """Returns a formatted datetime string, in YYYY-mm-ddTHH:mm:ssZ format."
  Example output: 2023-06-03T01:00:00Z
  """
  return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def SetMonthDateRangeAndTimeZone(targetTimeZone: str, localStartDateTime: datetime):
  """Sets the timezone and start/end times that will run when the retrieval function is run.\n 
  Used for one month reports.\n
  Returns:\n
  tz = (_UTCclass | StaticTzInfo | DstTzInfo),\n
  ltstart = datetime (local start time),\n
  ltend = datetime (local end time),\n
  utstart = datetime (UTC start time),\n
  utend = datetime (UTC end time)\n
  \n
  Usage Example:\n
  >>> tz, ltstart, ltend, utstart, utend = SetMonthDateRangeAndTimeZone("America/Los_Angeles", datetime(2023, 11, 1, 0, 0, 0))
  """
  #example: 2023-02-28T01:55:00Z
  # get the starting utc time and local time. This will set the tone for DST.
  tz = pytz.timezone(targetTimeZone)
  ltstart = tz.localize(localStartDateTime)
  utstart = ltstart.astimezone(pytz.utc)

  #Set to 31 days, as we don't have a months option for timedelta.
  td = timedelta(days = 31)
  utend = utstart + td

  # If the end date goes past the first of the following month (i.e. 28-30 day month), 
  # reset the end date to the first of the following month.
  # Also check to ensure the end hour is midnight in the event of daylight savings time.
  while utend.day > 1:
    utend = utend - timedelta(days = 1)

  # Initial assignment of local end time (exclusive) for DST check.
  ltend = utend.astimezone(tz)

  # Adjust for local daylight savings time changes if needed. Otherwise, continue.
  if ltstart.dst() and not ltend.dst():
    utend = utend + timedelta(hours = 1)
    ltend = utend.astimezone(tz)
  elif not ltstart.dst() and ltend.dst():
    utend = utend - timedelta(hours = 1)
    ltend = utend.astimezone(tz)

  return tz, ltstart, ltend, utstart, utend

def SetWeekDateRangeAndTimeZone(targetTimeZone: str, localStartDateTime: datetime):
  """Sets the timezone and start/end times that will run when the retrieval function is run.\n 
  Used for one week reports.\n
  Returns:\n
  tz = (_UTCclass | StaticTzInfo | DstTzInfo),\n
  ltstart = datetime (local start time),\n
  ltend = datetime (local end time),\n
  utstart = datetime (UTC start time),\n
  utend = datetime (UTC end time)\n
  \n
  Usage Example:\n
  >>> tz, ltstart, ltend, utstart, utend = SetWeekDateRangeAndTimeZone("America/Los_Angeles", datetime(2023, 11, 1, 0, 0, 0))
  """
  #example: 2023-02-28T01:55:00Z
  # get the starting utc time and local time. This will set the tone for DST.
  tz = pytz.timezone(targetTimeZone)
  ltstart = tz.localize(localStartDateTime)
  utstart = ltstart.astimezone(pytz.utc)

  #Set to 7 days, (one week).
  td = timedelta(days = 7)
  utend = utstart + td

  # Initial assignment of local end time (exclusive) for DST check.
  ltend = utend.astimezone(tz)

  # Adjust for local daylight savings time changes if needed. Otherwise, continue.
  if ltstart.dst() and not ltend.dst():
    utend = utend + timedelta(hours = 1)
    ltend = utend.astimezone(tz)
  elif not ltstart.dst() and ltend.dst():
    utend = utend - timedelta(hours = 1)
    ltend = utend.astimezone(tz)

  return tz, ltstart, ltend, utstart, utend