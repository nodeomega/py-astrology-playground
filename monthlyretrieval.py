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
# get the current utc time
tz = pytz.timezone("America/Los_Angeles")
ltstart = tz.localize(datetime(2023, 12, 1, 0, 0, 0))
utstart = ltstart.astimezone(pytz.utc)

#Set to 31 days, as we don't have a months option.
td = timedelta(days = 31)
ltend = ltstart + td

# If the end date goes past the first of the following month (i.e. 28-30 day month), 
# reset the end date to the first of the following month.
while ltend.day > 1:
  ltend = ltend - timedelta(days = 1)
utend = ltend.astimezone(pytz.utc)

#ut = datetime.now(timezone.utc)
utstring = FormatDateTimeString(utstart) # "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(utstart.year, utstart.month, utstart.day, utstart.hour, utstart.minute, utstart.second)

utendstring = FormatDateTimeString(utend) # "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(utend.year, utend.month, utend.day, utend.hour, utend.minute, utend.second)

print("Processing from {} - {}".format(ltstart, ltend))

activeut = utstart
inctd = timedelta(hours=1)
while (activeut < utend):
  utstring = FormatDateTimeString(activeut) # "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(activeut.year, activeut.month, activeut.day, activeut.hour, activeut.minute, activeut.second)

  #Get the data.
  # I'm running a local emulation of an azure function for this.
  print ("Processing {}...".format(utstring))
  api_url = "http://localhost:7071/api/ViewChart"
  reqparams = {
    "args":{
      "timestamp":utstring,
      "longitudeDeg":"122",
      "longitudeMin":"20",
      "longitudeSec":"0",
      "longitudeWE":"W",
      "latitudeDeg":"47",
      "latitudeMin":"36",
      "latitudeSec":"0",
      "latitudeNS":"N",
      "ignoreCusps":True,
      "ignoreAngles":True,
      "ignoreMinors":False,
      "includeStars":True,
      "planetSelection":"with asteroids",
      "maxOrb":"10",
      "asteroidSelection":"3811,128,157,7066"
      }
    }

  headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*'}
  response = requests.post(api_url, json=reqparams, headers=headers)

  print(response.status_code)
    
  if (response.status_code == 200):
    data = response.json()
    
    types = []
    for t in data["value"]["types"]:
      types.append(Type(t))

    aspectTypes = []
    for atype in data["value"]["aspectTypes"]:
      aspectTypes.append(AspectType(atype))

    bodies = []
    for b in data["value"]["bodies"]:
      thisBody = Body(b)
      thisBody.SetType([type for type in types if type.typeId == thisBody.typeId][0])
      bodies.append(thisBody)

    bodyCoordinates = []
    for bc in data["value"]["bodyCoordinates"]:
      targetBody = [body for body in bodies if body.id == bc["bodyId"]][0]
      thisBodyCoordinates = BodyCoordinates(targetBody, utstring, bc["coordinates"])
      bodyCoordinates.append(thisBodyCoordinates)
    
    aspectGroups = []
    for ag in data["value"]["aspectGroups"]:
      thisAspectGroup = AspectGroup(ag)
      thisAspectGroup.SetAspectType([atype for atype in aspectTypes if atype.id == thisAspectGroup.aspectTypeId][0])
      thisAspectGroup.SetBodies([b1 for b1 in bodies if b1.id == thisAspectGroup.body1Id][0], [b2 for b2 in bodies if b2.id == thisAspectGroup.body2Id][0])
      aspectGroups.append(thisAspectGroup)

    #ag: AspectGroup
    # for ag in aspectGroups:
    #   print ("{}: {} {} {}".format(ag.id, ag.body1.name, ag.aspectType.name, ag.body2.name))

    aspects = []
    for a in data["value"]["aspects"]:
      thisAspect = Aspect(a)
      thisAspect.SetAspectGroup([ag for ag in aspectGroups if ag.id == thisAspect.aspectGroupId][0])
      aspects.append(thisAspect)

    a: Aspect
    for a in aspects:
      #print ("{} {} {} {} {} (Orb {})".format(a.aspectGroup.body1.name, a.body1Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body2.name, a.body2Coordinates, a.orb))
      if (a.aspectGroup.aspectType.name not in ["Quindecile", "Novile", "Decile"]):
        if (ShouldFlipBodies(a.aspectGroup.body1.name, a.aspectGroup.body2.name) == True):
          allAspects.append(TimedAspect(utstring, a.aspectGroup.body2.name, a.body2Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body1.name, a.body1Coordinates, a.orb, a.orbDecimal))
        else:
          allAspects.append(TimedAspect(utstring, a.aspectGroup.body1.name, a.body1Coordinates, a.aspectGroup.aspectType.name, a.aspectGroup.body2.name, a.body2Coordinates, a.orb, a.orbDecimal))
    
    bc: BodyCoordinates
    for bc in bodyCoordinates:
      allBodies.append(TimedBody(utstring, bc.body.name, bc.coordinates))

  #increment to next timestamp.
  activeut = activeut + inctd

# Creates the output directory if it doesn't exist. Does nothing if present.
Path("monthlyout").mkdir(parents=True, exist_ok=True)

# Write the monthly aspects file.
with open("monthlyout\{:04d}-{:02d}-{:02d}-monthly-aspects-table.txt".format(utstart.year, utstart.month, utstart.day), "w", encoding="utf-8") as w:
  ta: TimedAspect
  for ta in allAspects:
    thisutc = datetime.fromisoformat(ta.timestamp.replace('Z', '+00:00'))
    thislocal = thisutc.astimezone(tz)
    w.write("{}: {} {} {} {} {} (Orb {})\n".format(thislocal, ta.body1Name, ta.body1Coordinates, ta.aspectName, ta.body2Name, ta.body2Coordinates, ta.orb))

# Write the monthly bodies sign/retrograde change file.
with open("monthlyout\{:04d}-{:02d}-{:02d}-monthly-bodies-table.txt".format(utstart.year, utstart.month, utstart.day), "w", encoding="utf-8") as w:
  tb: TimedBody
  for tb in allBodies:
    thisutc = datetime.fromisoformat(tb.timestamp.replace('Z', '+00:00'))
    thislocal = thisutc.astimezone(tz)
    w.write("{}: {} {}\n".format(thislocal, tb.bodyName, tb.coordinates))