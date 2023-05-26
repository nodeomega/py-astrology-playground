from functools import cmp_to_key
import re
from datetime import datetime, timedelta
from pathlib import Path

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

aspectPriority = {
  "Conjunct": 0,
  "Opposite": 1,
  "Square": 2,
  "Semisquare": 3,
  "Sesquiquadrate": 4,
  "Trine": 5,
  "Sextile": 6,
  "Quincunx": 7,
  "Semisextile": 8,
  "Quintile": 9,
  "Biquintile": 10,
  "Septile": 11,
  "Biseptile": 12,
  "Triseptile": 13,
  "Decile": 14,
  "Novile": 15,
  "Quindecile": 16
}

def CompareBodyNames(body1Name, body2Name):
  if (bodyPriority.get(body1Name) == None and bodyPriority.get(body2Name) == None):
    if (body1Name.lower() < body2Name.lower()):
      return -1
    elif (body1Name.lower() > body2Name.lower()):
      return 1
    else:
      return 0
  elif (bodyPriority.get(body1Name) != None and bodyPriority.get(body2Name) == None):
    return -1
  elif (bodyPriority.get(body1Name) == None and bodyPriority.get(body2Name) != None):
    return 1
  else:
    if (bodyPriority.get(body1Name) < bodyPriority.get(body2Name)):
      return -1
    elif (bodyPriority.get(body1Name) > bodyPriority.get(body2Name)):
      return 1
    else:
      return 0

def CompareAspectNames(aspect1Name, aspect2Name):
  if (aspectPriority.get(aspect1Name) == None and aspectPriority.get(aspect2Name) == None):
    if (aspect1Name.lower() < aspect2Name.lower()):
      return -1
    elif (aspect1Name.lower() > aspect2Name.lower()):
      return 1
    else:
      return 0
  elif (aspectPriority.get(aspect1Name) != None and aspectPriority.get(aspect2Name) == None):
    return -1
  elif (aspectPriority.get(aspect1Name) == None and aspectPriority.get(aspect2Name) != None):
    return 1
  else:
    if (aspectPriority.get(aspect1Name) < aspectPriority.get(aspect2Name)):
      return -1
    elif (aspectPriority.get(aspect1Name) > aspectPriority.get(aspect2Name)):
      return 1
    else:
      return 0

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
  
  def AddTimestamp(self, aspect: WeeklyInLine): #timestamp:datetime, orb:AspectOrb):
    added = False
    for t in self.timestamps:
      if t.timestampEnd == aspect.timestamp - timedelta(hours=1) and not added:
        t.AddToTimestamp(aspect) #timestamp, orb)
        added = True
    
    if not added:
      self.timestamps.append(TimestampRange(aspect)) #timestamp, orb))

class TimestampRange(object):
  timestampStart: datetime = None
  timestampEnd: datetime = None
  timestampTightestOrb: datetime = None
  tightestOrb:AspectOrb = None
  
  def __init__(self, aspect: WeeklyInLine): # timestamp, orb):
    self.timestampStart = aspect.timestamp
    self.timestampEnd = aspect.timestamp
    self.timestampTightestOrb = aspect.timestamp
    self.tightestOrb = aspect.orb    
  
  def AddToTimestamp(self, aspect: WeeklyInLine): #timestamp, orb:AspectOrb):
    self.timestampEnd = aspect.timestamp
    if (aspect.orb.orbDecimal < self.tightestOrb.orbDecimal):
      self.tightestOrb = aspect.orb
      self.timestampTightestOrb = aspect.timestamp

  def TimestampRange(self):
    return "{} to {}, tightest at {} ({})".format(self.timestampStart.strftime("%Y-%m-%d %H:%M:%S%z"), self.timestampEnd.strftime("%Y-%m-%d %H:%M:%S%z"), 
                                                  self.timestampTightestOrb.strftime("%Y-%m-%d %H:%M:%S%z"), self.tightestOrb.orb)

# 2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34" Square Saturn 06 Pis 52'20" (Orb 0°01'46")

aspectsDict = {}

with open("monthlyout\\2023-06-01-monthly.txt", "r", encoding="utf-8") as r:
  aspectsLog = r.readlines()

  for line in aspectsLog:
    aspectMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) ([a-zA-Z]{3,20}) ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) \(Orb (\d{1,2}°\d{2}\'\d{2}")\)', line)

    if aspectMatch:
      parsedAspectLine = WeeklyInLine(aspectMatch.group(1), aspectMatch.group(2), aspectMatch.group(3), aspectMatch.group(4), aspectMatch.group(5), aspectMatch.group(6), aspectMatch.group(7) == " Rx", aspectMatch.group(8),
                                      aspectMatch.group(9), aspectMatch.group(10), aspectMatch.group(11), aspectMatch.group(12), aspectMatch.group(13), aspectMatch.group(14) == " Rx", aspectMatch.group(15))
    
      aspectEntryText = "{} {} {}".format(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)
      if (aspectEntryText not in aspectsDict):
        aspectsDict[aspectEntryText] = Aspect(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)
      
      aspectsDict[aspectEntryText].AddTimestamp(parsedAspectLine)#.timestamp, parsedAspectLine.orb)

# sort by multiple fields.
aspectsDict = dict(sorted(aspectsDict.items(), key = cmp_to_key(lambda x, y: (CompareBodyNames(x[1].leftBodyName, y[1].leftBodyName) * 10000 + 
                                                                   CompareBodyNames(x[1].rightBodyName, y[1].rightBodyName) * 100 +
                                                                   CompareAspectNames(x[1].aspectName, y[1].aspectName)))))

Path("monthlyout").mkdir(parents=True, exist_ok=True)
with open("monthlyout\\2023-06-monthly-aspects.txt", "w", encoding="utf-8") as w:
  for a, v in aspectsDict.items():
    w.write("{}:\n".format(aspectsDict[a].Name()))
    for t in aspectsDict[a].timestamps:
      w.write("  {}\n".format(t.TimestampRange()))
    w.write("\n")