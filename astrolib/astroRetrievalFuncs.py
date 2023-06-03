from datetime import datetime


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