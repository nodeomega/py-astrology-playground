import requests
import json
import pytz

from datetime import datetime, timedelta, timezone
from pathlib import Path

class Body(object):
  name = ""
  typeId = 0
  id = 0
  type = None

  def __init__(self, body):
    super().__init__()
    self.name = body["name"]
    self.id = body["id"]
    self.typeId = body["typeId"]

  def SetType(self, type):
    self.type: Type = type
    self.typeId = type.typeId

class Type(object):
  type = ""
  typeId = 0

  def __init__(self, type):
    super().__init__()
    self.type = type["type"]
    self.typeId = type["typeId"]

class AspectType(object):
  name = ""
  id = 0

  def __init__(self, atype):
    super().__init__()
    self.name = atype["name"]
    self.id = atype["id"]

class AspectGroup(object):
  aspectTypeId = 0
  body1Id = 0
  body2Id = 0
  id = 0
  body1 = None
  body2 = None
  aspectType = None

  def __init__(self, ag):
    super().__init__()
    self.aspectTypeId = ag["aspectTypeId"]
    self.body1Id = ag["body1Id"]
    self.body2Id = ag["body2Id"]
    self.id = ag["id"]

  def SetBodies(self, body1, body2):
    self.body1: Body = body1
    self.body1Id = body1.id
    self.body2: Body = body2
    self.body2Id = body2.id

  def SetAspectType(self, atype):
    self.aspectType: AspectType = atype
    self.aspectTypeId = atype.id

class Aspect(object):
  aspectGroupId = 0
  aspectGroup = None
  body1Coordinates = ""
  body2Coordinates = ""
  orb = ""
  orbDecimal: float = 0.0

  def __init__(self, a):
    super().__init__()
    self.aspectGroupId = a["aspectGroupId"]
    self.body1Coordinates = a["body1Coordinates"]
    self.body2Coordinates = a["body2Coordinates"]
    self.orb = a["orb"]
    self.orbDecimal = a["orbDecimal"]

  def SetAspectGroup(self, ag: AspectGroup):
    self.aspectGroup: AspectGroup = ag
    self.aspectGroupId = ag.id

#print ("{} {} {} {} {} (Orb {})".format(a.aspectGroup.body1.name, a.body1Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body2.name, a.body2Coordinates, a.orb))
class TimedAspect(object):
  timestamp = ""
  body1Name = ""
  body1Coordinates = ""
  aspectName = ""
  body2Name = ""
  body2Coordinates = ""
  orb = ""
  orbDecimal: float = 0.0

  def __init__(self, timestamp, body1Name, body1Coordinates, aspectName, body2Name, body2Coordinates, orb, orbDecimal):
    super().__init__()
    self.timestamp = timestamp
    self.body1Name = body1Name
    self.body1Coordinates = body1Coordinates
    self.aspectName = aspectName
    self.body2Name = body2Name
    self.body2Coordinates = body2Coordinates
    self.orb = orb
    self.orbDecimal = orbDecimal

allAspects = []
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


#example: 2023-02-28T01:55:00Z
# get the current utc time
tz = pytz.timezone("America/Los_Angeles")
ltstart = tz.localize(datetime(2023, 3, 6, 0, 0, 0))
utstart = ltstart.astimezone(pytz.utc)
td = timedelta(days = 7)
ltend = ltstart + td
utend = ltend.astimezone(pytz.utc)

ut = datetime.now(timezone.utc)
utstring = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(utstart.year, utstart.month, utstart.day, utstart.hour, utstart.minute, utstart.second)
print (utstring)

utendstring = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(utend.year, utend.month, utend.day, utend.hour, utend.minute, utend.second)
print (utendstring)

print("{} - {}".format(ltstart, ltend))

activeut = utstart
inctd = timedelta(hours=1)
while (activeut < utend):
  utstring = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(activeut.year, activeut.month, activeut.day, activeut.hour, activeut.minute, activeut.second)

  print ("Processing {}...".format(utstring))
  api_url = "http://localhost:7071/api/ViewChart"
  reqparams = {"args":{"timestamp":utstring,"longitudeDeg":"122","longitudeMin":"20","longitudeSec":"0","longitudeWE":"W","latitudeDeg":"47","latitudeMin":"36","latitudeSec":"0","latitudeNS":"N","ignoreCusps":True,"ignoreAngles":True,"ignoreMinors":False,"includeStars":True,"planetSelection":"with asteroids","maxOrb":"10","asteroidSelection":"3811"}}

  headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*'}
  response = requests.post(api_url, json=reqparams, headers=headers)

  print(response.status_code)
    
  if (response.status_code == 200):
    data = response.json()
    
    types = []
    for t in data["value"]["types"]:
      types.append(Type(t))

    # for t in types:
    #   print("{} {}".format(t.type, t.typeId))

    aspectTypes = []
    for atype in data["value"]["aspectTypes"]:
      aspectTypes.append(AspectType(atype))

    bodies = []
    for b in data["value"]["bodies"]:
      thisBody = Body(b)
      thisBody.SetType([type for type in types if type.typeId == thisBody.typeId][0])
      bodies.append(thisBody)
    
    # for b in bodies:
    #   print("{} {} {} {}".format(b.name, b.id, b.typeId, b.type.type))

    aspectGroups = []
    for ag in data["value"]["aspectGroups"]:
      thisAspectGroup = AspectGroup(ag)
      thisAspectGroup.SetAspectType([atype for atype in aspectTypes if atype.id == thisAspectGroup.aspectTypeId][0])
      thisAspectGroup.SetBodies([b1 for b1 in bodies if b1.id == thisAspectGroup.body1Id][0], [b2 for b2 in bodies if b2.id == thisAspectGroup.body2Id][0])
      aspectGroups.append(thisAspectGroup)

    ag: AspectGroup
    for ag in aspectGroups:
      print ("{}: {} {} {}".format(ag.id, ag.body1.name, ag.aspectType.name, ag.body2.name))

    aspects = []
    for a in data["value"]["aspects"]:
      thisAspect = Aspect(a)
      thisAspect.SetAspectGroup([ag for ag in aspectGroups if ag.id == thisAspect.aspectGroupId][0])
      aspects.append(thisAspect)

    a: Aspect
    for a in aspects:
      print ("{} {} {} {} {} (Orb {})".format(a.aspectGroup.body1.name, a.body1Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body2.name, a.body2Coordinates, a.orb))
      if (a.aspectGroup.aspectType.name not in ["Quindecile", "Novile", "Decile"]):
        if (ShouldFlipBodies(a.aspectGroup.body1.name, a.aspectGroup.body2.name) == True):
          allAspects.append(TimedAspect(utstring, a.aspectGroup.body2.name, a.body2Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body1.name, a.body1Coordinates, a.orb, a.orbDecimal))
        else:
          allAspects.append(TimedAspect(utstring, a.aspectGroup.body1.name, a.body1Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body2.name, a.body2Coordinates, a.orb, a.orbDecimal))
  activeut = activeut + inctd

Path("weeklyout").mkdir(parents=True, exist_ok=True)
with open("weeklyout\{:04d}-{:02d}-{:02d}-weekly.txt".format(utstart.year, utstart.month, utstart.day), "w", encoding="utf-8") as w:
  ta: TimedAspect
  for ta in allAspects:
    thisutc = datetime.fromisoformat(ta.timestamp.replace('Z', '+00:00'))
    thislocal = thisutc.astimezone(tz) #tz.localize(thisutc)
    w.write("{}: {} {} {} {} {} (Orb {})\n".format(thislocal, ta.body1Name, ta.body1Coordinates, ta.aspectName, ta.body2Name, ta.body2Coordinates, ta.orb))

print (ShouldFlipBodies("Pluto", "Sun"))