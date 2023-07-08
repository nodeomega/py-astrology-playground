from functools import cmp_to_key
import re
from datetime import datetime, timedelta

processDateTime = datetime(2023, 7, 1, 0, 0, 0)

aspectCalendarLines = {}

class AspectCalendarLine(object):
  aspect = ""
  dates = []
  peakDates = []

  def __init__(self, aspect):
    self.aspect = aspect
    self.dates = []
    self.peakDates = []

  def EarliestDate(self):
    if len(self.dates) <= 0:
      return None
    return self.dates[0]
  
  def LastDate(self):
    if len(self.dates) <= 0:
      return None
    return self.dates[len(self.dates) - 1]
  
  def PeakDate(self):
    """Returns the first peak date."""
    if len(self.peakDates) <= 0:
      return None
    return self.peakDates[0]

def CompareDateStrings(ds1, ds2):
  if (ds1 != None and ds2 == None):
    return -1
  elif (ds1 == None and ds2 != None):
    return 1
  elif (ds1 == None and ds2 == None):
    return 0
  else:
    if (ds1 < ds2):
      return -1
    elif (ds1 > ds2):
      return 1
    else:
      return 0

class BodyChangeLogItem(object):
   timestampString = ""
   description = ""

   def __init__(self, timestampString, description):
     self.timestampString = timestampString
     self.description = description

ignoreAspects = ["Decile", "Novile", "Quintile", "Biquintile", "Septile", "Biseptile", "Triseptile", "Quindecile"]

with open("monthlyout\\{:04d}-{:02d}-monthly-aspects.txt".format(processDateTime.year, processDateTime.month), "r", encoding="utf-8") as r:
  aspectTimeLog = r.readlines()

  currentLine = ""
  for line in aspectTimeLog:
    
    timeMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}) to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}), tightest at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}) \((\d{1,2}°\d{2}\'\d{2}")\)', line)
    if timeMatch:
      startdt = datetime.strptime(timeMatch.group(1), "%Y-%m-%d %H:%M:%S%z")
      enddt = datetime.strptime(timeMatch.group(2), "%Y-%m-%d %H:%M:%S%z")
      peakdt = datetime.strptime(timeMatch.group(3), "%Y-%m-%d %H:%M:%S%z")

      startdate = datetime(startdt.year, startdt.month, startdt.day)
      enddate = datetime(enddt.year, enddt.month, enddt.day)
      peakdate = datetime(peakdt.year, peakdt.month, peakdt.day)

      currentdate = startdate
      while currentdate <= enddate:
        calendarDateString = "{:04d}-{:02d}-{:02d}".format(currentdate.year, currentdate.month, currentdate.day)
        
        if not any(i in currentLine for i in ignoreAspects):
          aspectCalendarLines[currentLine.strip(":\n").strip()].dates.append(calendarDateString)
          if (currentdate == peakdate):
            aspectCalendarLines[currentLine.strip(":\n").strip()].peakDates.append(calendarDateString)

        currentdate = currentdate + timedelta(days=1)
    else:
      currentLine = line
      if currentLine.strip(":").strip() not in aspectCalendarLines and line.strip():
        aspectCalendarLines[currentLine.strip(":\n").strip()] = AspectCalendarLine(currentLine.strip(":\n").strip())

bodyChangeLog = {}
bodyChangeLogForTable = {}

with open("monthlyout\\{:04d}-{:02d}-monthly-sign-retrograde-changes.txt".format(processDateTime.year, processDateTime.month), "r", encoding="utf-8") as r:
  bodyTimeLog = r.readlines()

  for line in bodyTimeLog:
    changeMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}:\d{2}): ([a-zA-Z0-9\s\*\-\']+)\n', line)
    if changeMatch:
      #reformattedDateTime = changeMatch.group(1).replace("-07:00", "-0700").replace("-08:00", "-0800")
      bodyChangeLog[changeMatch.group(1)] = "{}: {}".format(changeMatch.group(1), changeMatch.group(2))
      bodyChangeLogForTable["{}-{}".format(changeMatch.group(1), changeMatch.group(2))] = BodyChangeLogItem(changeMatch.group(1), changeMatch.group(2))
      #print("{}: {}".format(changeMatch.group(1), changeMatch.group(2)))

nextMonth = processDateTime + timedelta(days=31)
endDateTime = datetime(nextMonth.year, nextMonth.month, 1)

numDays = endDateTime - processDateTime

targetBodies = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

with open("monthlyout\\{:04d}-{:02d}-monthly-calendar.html".format(processDateTime.year, processDateTime.month), "w", encoding="utf-8") as w:
  w.write("<!DOCTYPE html>\n")
  w.write("<html><head><title>TEST</title>")
  w.write(r"<style>")
  w.write(r"body {font-family: \"Century Gothic\", sans-serif} ")
  w.write(r"table, td, th {border: 1px solid;} ")
  w.write(r"table {position: relative; border-collapse: collapse; width: 100%; max-width:60vw; margin:0 auto;} ")
  w.write(r".active {background-color: #009900;}" )
  w.write(r".peak {background-color: #00ff00;}" )
  w.write(r"thead tr, tfoot tr {position:sticky; background-color:white}" )
  w.write(r"thead tr {top: 0}" )
  w.write(r"tfoot tr {bottom: 0}" )
  w.write(r"tr:hover {background-color: #dddddd}" )
  w.write(r"</style>")
  w.write("</head>")
  w.write("<body>")
  w.write("<table>")
  w.write("<thead><tr>")
  w.write("<th>Aspect</th>")

  for x in range(1, numDays.days + 1):
    w.write("<th>{}</th>".format(x))

  w.write("</tr></thead>")

  w.write("<tfoot><tr>")
  w.write("<th>Aspect</th>")

  for x in range(1, numDays.days + 1):
    w.write("<th>{}</th>".format(x))

  w.write("</tr></tfoot>")
  w.write("<tbody>")
  
  # sort by earliest date and last date for the month that the aspect occurs.  
  aspectCalendarLines = dict(sorted(aspectCalendarLines.items(), key = cmp_to_key(lambda x, y: CompareDateStrings(x[1].EarliestDate(), y[1].EarliestDate()) * 1000 +
                                                                                  CompareDateStrings(x[1].PeakDate(), y[1].PeakDate()) * 10000 +
                                                                                  CompareDateStrings(x[1].LastDate(), y[1].LastDate()) * 100)))
  
  v: AspectCalendarLine
  for a, v in aspectCalendarLines.items():
    if any(i in v.aspect for i in ignoreAspects) or (v.aspect[0:4] == "Moon") or not any(t in v.aspect for t in targetBodies):
      continue
    w.write("<tr>")
    w.write("<td>{}</td>".format(v.aspect))
    for x in range(1, numDays.days + 1):
      if any(datetime.strptime(d, "%Y-%m-%d").day == x for d in v.peakDates):
        w.write("<td class=\"peak\">{}</td>".format(" "))
      elif any(datetime.strptime(d, "%Y-%m-%d").day == x for d in v.dates): # datetime.strptime(d, "%Y-%m-%d").day == x: # and v in v2:
        w.write("<td class=\"active\">{}</td>".format(" "))
      else:
        w.write("<td>{}</td>".format(" "))          
    w.write("</tr>")
  w.write("</tbody>")
  w.write("</table>")

  bodyChangeLog = dict(sorted(bodyChangeLog.items(), key = lambda item: item[1]))
  bodyChangeLogForTable = dict(sorted(bodyChangeLogForTable.items(), key = lambda item: item[1].timestampString))

  #w.write("<ul>")
  w.write("<table>")
  w.write("<thead><tr>")
  w.write("<th>Timestamp</th>")
  w.write("<th>Sign or Direction Change</th>")
  w.write("</tr></thead>")
  w.write("<tfoot><tr>")
  w.write("<th>Timestamp</th>")
  w.write("<th>Sign or Direction Change</th>")
  w.write("</tr></tfoot>")
  w.write("<tbody>")

  # for b, v in bodyChangeLog.items():
  #   w.write("<li>{}</li>".format(v))
  v: BodyChangeLogItem
  for b, v in bodyChangeLogForTable.items():
    w.write("<tr><td>{}</td><td>{}</td></tr>".format(v.timestampString, v.description))

  #w.write("</ul>")
  w.write("</tbody>")
  w.write("</table>")

  w.write("</body></html>")