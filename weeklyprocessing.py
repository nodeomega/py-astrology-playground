import requests
import json
import pytz
import re
from datetime import datetime, timedelta

SignDeg = {
  "Ari": 0,
  "Tau": 30,
  "Gem": 60,
  "Can": 90,
  "Leo": 120,
  "Vir": 150,
  "Lib": 180,
  "Sco": 210,
  "Sag": 240,
  "Cap": 270,
  "Aqu": 300,
  "Pis": 330
}

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

class BodyInfo(object):
  name = ""
  degrees = 0
  sign = ""
  minutes = 0
  seconds = 0
  isRetrograde = False

  def __init__(self, name, degrees, sign, minutes, seconds, isRetrograde):
    super().__init__()
    self.name = name
    self.degree = degrees
    self.sign = sign
    self.minutes = minutes
    self.seconds = seconds
    self.isRetrograde = isRetrograde

  def CoordinatesDecimal(self) -> float:
    return (self.degree + SignDeg[self.sign]) + (self.minutes / 60) + (self.seconds / 3600)

class AspectOrb(object):
  orb = ""
  orbDecimal:float = 0

  def __init__(self, orb):
    self.orb = orb
    orbRegexMatch = re.search(r'(\d{1,2})°(\d{2})\'(\d{2})"', orb)
    if orbRegexMatch:
      self.orbDecimal = float(orbRegexMatch.group(1)) + (float(orbRegexMatch.group(2)) / 60) + (float(orbRegexMatch.group(3)) / 3600)

class WeeklyInLine(object):
  timestampString = ""
  timestamp: datetime = None
  leftBody: BodyInfo = None
  aspectName =  ""
  rightBody: BodyInfo = None
  orb:AspectOrb = None  

  def __init__(self, timestamp, leftName, leftDegrees, leftSign, leftMinutes, leftSeconds, leftIsRetrograde, aspectName, rightName, rightDegrees, rightSign, rightMinutes, rightSeconds, rightIsRetrograde, orb):
    self.timestampString = timestamp
    # 2023-05-28 03:00:00-07:00
    if ":" == timestamp[-3:-2]:
      timestamp = timestamp[:-3]+timestamp[-2:]
    self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z")
    self.leftBody = BodyInfo(leftName, leftDegrees, leftSign, leftMinutes, leftSeconds, leftIsRetrograde)
    self.aspectName = aspectName
    self.rightBody = BodyInfo(rightName, rightDegrees, rightSign, rightMinutes, rightSeconds, rightIsRetrograde)
    self.orb = AspectOrb(orb)
  
class Aspect(object):
  leftBodyName = ""
  aspectName = ""
  rightBodyName = ""
  timestamps = []

  def __init__(self, leftBodyName, aspectName, rightBodyName):
    self.leftBodyName = leftBodyName
    self.aspectName = aspectName
    self.rightBodyName = rightBodyName
    self.timestamps = []

  def Name(self):
    return ("{} {} {}".format(self.leftBodyName, self.aspectName, self.rightBodyName))
  
  def AddTimestamp(self, timestamp:datetime, orb:AspectOrb):
    added = False
    for t in self.timestamps:
      if t.timestampEnd == timestamp - timedelta(hours=1) and not added:
        t.AddToTimestamp(timestamp, orb)
        added = True
    
    if not added:
      self.timestamps.append(TimestampRange(timestamp, orb))

class TimestampRange(object):
  timestampStart: datetime = None
  timestampEnd: datetime = None
  timestampTightestOrb: datetime = None
  tightestOrb:AspectOrb = None
  
  def __init__(self, timestamp, orb):
    self.timestampStart = timestamp
    self.timestampEnd = timestamp
    self.timestampTightestOrb = timestamp
    self.tightestOrb = orb    
  
  def AddToTimestamp(self, timestamp, orb:AspectOrb):
    self.timestampEnd = timestamp
    if (orb.orbDecimal < self.tightestOrb.orbDecimal):
      self.tightestOrb = orb
      self.timestampTightestOrb = timestamp

  def TimestampRange(self):
    return "{} to {}, tightest at {} ({})".format(self.timestampStart.strftime("%Y-%m-%d %H:%M:%S%z"), self.timestampEnd.strftime("%Y-%m-%d %H:%M:%S%z"), 
                                                  self.timestampTightestOrb.strftime("%Y-%m-%d %H:%M:%S%z"), self.tightestOrb.orb)

# 2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34" Square Saturn 06 Pis 52'20" (Orb 0°01'46")
# testIn = "2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34\" Square Saturn 06 Pis 52'20\" (Orb 0°01'46\")"
# testMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) ([a-zA-Z]{3,20}) ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) \(Orb (\d{1,2}°\d{2}\'\d{2}")\)', testIn)

# if testMatch:
#   print(testMatch.group())
#   print ("parse succeed")
# else:
#   print (testIn)
#   print ("parse failed")
# test2 = WeeklyInLine(testMatch.group(1), testMatch.group(2), testMatch.group(3), testMatch.group(4), testMatch.group(5), testMatch.group(6), testMatch.group(7) == " Rx", testMatch.group(8),
#                      testMatch.group(9), testMatch.group(10), testMatch.group(11), testMatch.group(12), testMatch.group(13), testMatch.group(14) == " Rx", testMatch.group(15))

aspectsDict = {}

with open("weeklyout\\2023-05-22-weekly.txt", "r", encoding="utf-8") as r:
  aspectsLog = r.readlines()

  for line in aspectsLog:
    aspectMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) ([a-zA-Z]{3,20}) ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) \(Orb (\d{1,2}°\d{2}\'\d{2}")\)', line)

    if aspectMatch:
      parsedAspectLine = WeeklyInLine(aspectMatch.group(1), aspectMatch.group(2), aspectMatch.group(3), aspectMatch.group(4), aspectMatch.group(5), aspectMatch.group(6), aspectMatch.group(7) == " Rx", aspectMatch.group(8),
                                      aspectMatch.group(9), aspectMatch.group(10), aspectMatch.group(11), aspectMatch.group(12), aspectMatch.group(13), aspectMatch.group(14) == " Rx", aspectMatch.group(15))
    
      aspectEntryText = "{} {} {}".format(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)
      if (aspectEntryText not in aspectsDict):
        aspectsDict[aspectEntryText] = Aspect(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)
      
      aspectsDict[aspectEntryText].AddTimestamp(parsedAspectLine.timestamp, parsedAspectLine.orb)

#aspectsDict = sorted(aspectsDict, key = lambda x: (x.leftBodyName, x.rightBodyName))

for a, v in aspectsDict.items():
  print("{}: {} timestamps".format(aspectsDict[a].Name(), len(aspectsDict[a].timestamps)))
  for t in aspectsDict[a].timestamps:
    print("{}".format(t.TimestampRange()))