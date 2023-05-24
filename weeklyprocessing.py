import requests
import json
import pytz
import re
from datetime import datetime

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
  foo = 0

test = AspectOrb("1°23'37\"")

print (test)
print (test.orb)
print (test.orbDecimal)

# 2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34" Square Saturn 06 Pis 52'20" (Orb 0°01'46")
testIn = "2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34\" Square Saturn 06 Pis 52'20\" (Orb 0°01'46\")"
testMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) ([a-zA-Z]{3,20}) ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) \(Orb (\d{1,2}°\d{2}\'\d{2}")\)', testIn)

if testMatch:
  print(testMatch.group())
  print ("parse succeed")
else:
  print (testIn)
  print ("parse failed")
test2 = WeeklyInLine(testMatch.group(1), testMatch.group(2), testMatch.group(3), testMatch.group(4), testMatch.group(5), testMatch.group(6), testMatch.group(7) == " Rx", testMatch.group(8),
                     testMatch.group(9), testMatch.group(10), testMatch.group(11), testMatch.group(12), testMatch.group(13), testMatch.group(14) == " Rx", testMatch.group(15))


a = "2023-05-28 03:00:00-07:00: Sun 06 Gem 50'34\" Square Saturn 06 Pis 52'20\""
am = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3}) ([a-zA-Z]{3,20}) ([a-zA-Z0-9\s]+) (\d{2}) ([a-zA-Z]{3}) (\d{2})\'(\d{2}")([a-zA-Z\s]{0,3})', a)
if am:
  print(am)
  print ("parse succeed")
else:
  print (a)
  print ("parse failed")


