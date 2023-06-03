class Type(object):
  """Type object - from API output."""
  type = ""
  typeId = 0

  def __init__(self, type):
    super().__init__()
    self.type = type["type"]
    self.typeId = type["typeId"]

class Body(object):
  """Body object - from API output."""
  name = ""
  typeId = 0
  id = 0
  type = None

  def __init__(self, body):
    super().__init__()
    self.name = body["name"]
    self.id = body["id"]
    self.typeId = body["typeId"]

  def SetType(self, type: Type):
    self.type: Type = type
    self.typeId = type.typeId

class BodyCoordinates(object):
  body: Body = None
  timestamp = ""
  coordinates = ""

  def __init__(self, body: Body, timestamp, coordinates):
    self.body = body
    self.timestamp = timestamp
    self.coordinates = coordinates

class AspectType(object):
  """AspectType object - from API output."""
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
  """Aspect object - from API output."""
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

class TimedCoordinates(object):
  timestamp = ""
  bodyName = ""
  coordinates = ""
  
  def __init__(self, timestamp, bodyName, coordinates):
    self.timestamp = timestamp
    self.bodyName = bodyName
    self.coordinates = coordinates

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

class TimedBody(object):
  timestamp = ""
  bodyName = ""
  coordinates = ""

  def __init__(self, timestamp, bodyName, coordinates):
    self.timestamp = timestamp
    self.bodyName = bodyName
    self.coordinates = coordinates