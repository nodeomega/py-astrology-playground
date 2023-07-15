from functools import cmp_to_key
import re
from datetime import datetime, timedelta
from pathlib import Path
import pytz

from astrolib.astroProcessingConstants import SignDeg, SignFullNames, bodyPriority, aspectPriority

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

class AspectInLine(object):
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
    self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z")
    if " Rx" == leftName[-3:]:
      leftName = leftName[:-3]
    self.leftBody = BodyInfo(leftName, leftDegrees, leftSign, leftMinutes, leftSeconds, leftIsRetrograde)
    self.aspectName = aspectName
    if " Rx" == rightName[-3:]:
      rightName = rightName[:-3]
    self.rightBody = BodyInfo(rightName, rightDegrees, rightSign, rightMinutes, rightSeconds, rightIsRetrograde)
    self.orb = AspectOrb(orb)

class AspectTimestampRange(object):
  timestampStart: datetime = None
  timestampEnd: datetime = None
  timestampTightestOrb: datetime = None
  tightestOrb:AspectOrb = None
  tz = pytz.timezone("America/Los_Angeles")
  
  def __init__(self, aspect: AspectInLine): # timestamp, orb):
    self.timestampStart = aspect.timestamp
    self.timestampEnd = aspect.timestamp
    self.timestampTightestOrb = aspect.timestamp
    self.tightestOrb = aspect.orb    
  
  def AddToTimestamp(self, aspect: AspectInLine): #timestamp, orb:AspectOrb):
    self.timestampEnd = aspect.timestamp
    if (aspect.orb.orbDecimal < self.tightestOrb.orbDecimal):
      self.tightestOrb = aspect.orb
      self.timestampTightestOrb = aspect.timestamp

  def TimestampRange(self):
    ltstart = self.timestampStart
    utstart = ltstart.astimezone(pytz.utc)

    ltend = self.timestampEnd
    utend = ltend.astimezone(pytz.utc)

    ltpeak = self.timestampTightestOrb
    utpeak = ltpeak.astimezone(pytz.utc)

    # return "{} to {}, tightest at {} ({})".format(self.timestampStart.strftime("%Y-%m-%d %H:%M%z"), self.timestampEnd.strftime("%Y-%m-%d %H:%M%z"), 
    #                                               self.timestampTightestOrb.strftime("%Y-%m-%d %H:%M%z"), self.tightestOrb.orb)
    return "{} UTC to {} UTC, tightest at {} UTC ({})".format(utstart.strftime("%Y-%m-%d %H:%M"), utend.strftime("%Y-%m-%d %H:%M"), 
                                                  utpeak.strftime("%Y-%m-%d %H:%M"), self.tightestOrb.orb)

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
  
  def AddTimestamp(self, aspect: AspectInLine): #timestamp:datetime, orb:AspectOrb):
    added = False
    for t in self.timestamps:
      if t.timestampEnd == aspect.timestamp - timedelta(hours=1) and not added:
        t.AddToTimestamp(aspect) #timestamp, orb)
        added = True
    
    if not added:
      self.timestamps.append(AspectTimestampRange(aspect)) #timestamp, orb))

comparisonBodyNames = "Mars-Saturn"

infileNames = [
  "{} 1850-1874.txt".format(comparisonBodyNames),
  "{} 1875-1899.txt".format(comparisonBodyNames),
  "{} 1900-1924.txt".format(comparisonBodyNames),
  "{} 1925-1949.txt".format(comparisonBodyNames),
  "{} 1950-1974.txt".format(comparisonBodyNames),
  "{} 1975-1999.txt".format(comparisonBodyNames),
  "{} 2000-2024.txt".format(comparisonBodyNames),
  "{} 2025-2049.txt".format(comparisonBodyNames)
  ]

aspectsDict = {}

for file in infileNames:
  print ("processing {}...".format("infiles\\{}".format(file)))
  with open("infiles\\{}".format(file), "r", encoding="utf-8") as r:
    aspectsLog = r.readlines()

    for line in aspectsLog:
      aspectMatch = re.search(r'[a-zA-Z]{3} (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [\+\-]\d{2}:\d{2})\t([a-zA-Z0-9\s\*\-\']+)([a-zA-Z\s]{0,3})\t(\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3})\t([a-zA-Z]{3,20})\t([a-zA-Z0-9\s\*\-\']+)([a-zA-Z\s]{0,3})\t(\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3})\t(\d{1,2}°\d{2}\'\d{2}")', line)

      if aspectMatch:
        #print(aspectMatch.group(2))
        parsedAspectLine = AspectInLine(aspectMatch.group(1), aspectMatch.group(2), aspectMatch.group(4), aspectMatch.group(5), aspectMatch.group(6), aspectMatch.group(7), aspectMatch.group(8) == " Rx", aspectMatch.group(9),
                                      aspectMatch.group(10), aspectMatch.group(12), aspectMatch.group(13), aspectMatch.group(14), aspectMatch.group(15), aspectMatch.group(16) == " Rx", aspectMatch.group(17))
        
        aspectEntryText = "{} {} {}".format(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)
        #print (aspectEntryText)
        if (aspectEntryText not in aspectsDict):
          aspectsDict[aspectEntryText] = Aspect(parsedAspectLine.leftBody.name, parsedAspectLine.aspectName, parsedAspectLine.rightBody.name)        
        
        aspectsDict[aspectEntryText].AddTimestamp(parsedAspectLine)#.timestamp, parsedAspectLine.orb)
        #break
      else:
        # catch the failing line, and end the run.
        print("fail")
        print(line)
        break

# sort by multiple fields.
# Still needed as we're comparing the aspect names.
aspectsDict = dict(sorted(aspectsDict.items(), key = cmp_to_key(lambda x, y: (CompareBodyNames(x[1].leftBodyName, y[1].leftBodyName) * 10000 + 
                                                                   CompareBodyNames(x[1].rightBodyName, y[1].rightBodyName) * 100 +
                                                                   CompareAspectNames(x[1].aspectName, y[1].aspectName)))))

Path("two-bodies-out").mkdir(parents=True, exist_ok=True)
with open("two-bodies-out\\{}-aspects-listing.txt".format(comparisonBodyNames), "w", encoding="utf-8") as w:
  for a, v in aspectsDict.items():
    w.write("{}:\n".format(aspectsDict[a].Name()))
    for t in aspectsDict[a].timestamps:
      w.write("  {}\n".format(t.TimestampRange()))
    w.write("\n")