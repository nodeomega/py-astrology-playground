import requests
import pytz

from datetime import datetime, timedelta, timezone
from pathlib import Path

#import all of the types from astroRetrievalTypes
from astrolib.astroRetrievalTypes import *
from astrolib.astroRetrievalFuncs import ShouldFlipBodies, FormatDateTimeString

allAspects = []
allBodies = []

#example: 2023-02-28T01:55:00Z
# get the starting utc time and local time. This will set the tone for DST.
tz = pytz.timezone("America/Los_Angeles")
ltstart = tz.localize(datetime(2023, 3, 1, 0, 0, 0))
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

utstring = FormatDateTimeString(utstart) 

utendstring = FormatDateTimeString(utend)

print("Processing from {} - {}".format(ltstart, ltend))
print ("UTC: {} - {}".format(utstart, utend))
print ("DST: {} - {}".format(ltstart.dst(), ltend.dst()))

def SetDateRangeAndTimeZone(targetTimeZone: str, localStartDateTime: datetime):
  """
  Sets the timezone and start/end times that will run when the retrieval function is run.\n 
  Returns:\n
  tz = (_UTCclass | StaticTzInfo | DstTzInfo),\n
  ltstart = datetime (local start time),\n
  ltend = datetime (local end time),\n
  utstart = datetime (UTC start time),\n
  utend = datetime (UTC end time)\n
  \n
  Usage Example:\n
  >>> tz, ltstart, ltend, utstart, utend = SetDateRangeAndTimeZone("America/Los_Angeles", datetime(2023, 11, 1, 0, 0, 0))
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

for dt in [datetime(2023, 3, 1, 0, 0, 0), datetime(2023, 8, 1, 0, 0, 0), datetime(2023, 11, 1, 0, 0, 0), datetime(2023, 12, 1, 0, 0, 0)]:
  tz, ltstart, ltend, utstart, utend = SetDateRangeAndTimeZone("America/Los_Angeles", dt)
  utstring = FormatDateTimeString(utstart) 
  utendstring = FormatDateTimeString(utend)
  
  print("Processing from {} - {}".format(ltstart, ltend))
  print ("UTC: {} - {}".format(utstart, utend))
  print ("DST: {} - {}".format(ltstart.dst(), ltend.dst()))