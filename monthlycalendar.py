from functools import cmp_to_key
import re
from datetime import datetime, timedelta
from pathlib import Path

processDateTime = datetime(2023, 6, 1, 0, 0, 0)

calendarDays = {}
aspects = {}

ignoreAspects = ["Decile", "Novile", "Quintile", "Biquintile", "Septile", "Biseptile", "Triseptile", "Quindecile"]

with open("monthlyout\\{:04d}-{:02d}-monthly-aspects.txt".format(processDateTime.year, processDateTime.month), "r", encoding="utf-8") as r:
  aspectTimeLog = r.readlines()

  currentLine = ""
  for line in aspectTimeLog:
    
    timeMatch = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}) to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}), tightest at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\+\-]\d{2}\d{2}) \((\d{1,2}°\d{2}\'\d{2}")\)', line)
    if timeMatch:
      startdt = datetime.strptime(timeMatch.group(1), "%Y-%m-%d %H:%M:%S%z")
      enddt = datetime.strptime(timeMatch.group(2), "%Y-%m-%d %H:%M:%S%z")
      tightestdt = datetime.strptime(timeMatch.group(3), "%Y-%m-%d %H:%M:%S%z")

      startdate = datetime(startdt.year, startdt.month, startdt.day)
      enddate = datetime(enddt.year, enddt.month, enddt.day)
      tightestdate = datetime(tightestdt.year, tightestdt.month, tightestdt.day)

      currentdate = startdate
      while currentdate <= enddate:
        calendarDateString = "{:04d}-{:02d}-{:02d}".format(currentdate.year, currentdate.month, currentdate.day)
        if calendarDateString not in calendarDays:
          calendarDays[calendarDateString] = ""
        
        if not any(i in currentLine for i in ignoreAspects):
          calendarDays[calendarDateString] = calendarDays[calendarDateString] + currentLine.strip(":\n") + "\n"
        currentdate = currentdate + timedelta(days=1)

      #print ("{} to {}, closest {}".format(startdt, enddt, tightestdt))
      #print ("match")
    else:
      currentLine = line
      if currentLine.strip(":").strip() not in aspects and line.strip():
        aspects[currentLine.strip(":\n").strip()] = currentLine.strip(":\n").strip()
      #print (currentLine.replace("\n", ""))

calendarDays = dict(sorted(calendarDays.items()))
longestItem = max(aspects, key=len)

nextMonth = processDateTime + timedelta(days=31)
endDateTime = datetime(nextMonth.year, nextMonth.month, 1)

# firstLine = ""
# secondLine = ""
# for x in range(0, len(longestItem)):
#   firstLine = firstLine + " "
#   secondLine = secondLine + " "

# firstLine = firstLine + "  "
# secondLine = secondLine + "  "

# numDays = endDateTime - processDateTime

# for x in range(1, numDays.days + 1):
#   firstLine = firstLine + ("{:02d}".format(x))[0]
#   secondLine = secondLine  + ("{:02d}".format(x))[1]

# for c, v in calendarDays.items():
#   print ("{}:".format(c))
#   print (v)

# for a, v in aspects.items():
#   print(v)

# print (firstLine)
# print (secondLine)

for a, v in aspects.items():
  if any(i in v for i in ignoreAspects):
    continue
  curLine = "{}".format(v).ljust(len(longestItem) + 2)
  for x in range(1, numDays.days + 1):
    for c, w in calendarDays.items():
      if datetime.strptime(c, "%Y-%m-%d").day == x and v in w:
        curLine = curLine + "X"
      elif datetime.strptime(c, "%Y-%m-%d").day == x and v not in w:
        curLine = curLine + " "
  #curLine = curLine + "\n"
  print (curLine)
  # print ("{}:".format(c))
  # print (v)

targetBodies = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

with open("monthlyout\\{:04d}-{:02d}-monthly-calendar.html".format(processDateTime.year, processDateTime.month), "w", encoding="utf-8") as w:
  w.write("<!DOCTYPE html>\n")
  w.write("<html><head><title>TEST</title>")
  w.write(r"<style>")
  w.write(r"body {font-family: \"Century Gothic\", sans-serif} ")
  w.write(r"table, td, th {border: 1px solid;} ")
  w.write(r"table {position: relative; border-collapse: collapse; width: 100%; max-width:60vw; margin:0 auto;} ")
  w.write(r".active {background-color: #009900}" )
  w.write(r"thead tr, tfoot tr {position:sticky; background-color:white}" )
  w.write(r"thead tr {top: 0}" )
  w.write(r"tfoot tr {bottom: 0}" )
  w.write(r"tr:hover {background-color: #dddddd}" )
  w.write(r"</style>")
  w.write("</head>")
  w.write("<body>")
  #w.write("<h1>This is a test</h1>")
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
  for a, v in aspects.items():
    if any(i in v for i in ignoreAspects) or (v[0:4] == "Moon") or not any(t in v for t in targetBodies):
      continue
    #print (v[0:4])
    w.write("<tr>")
    w.write("<td>{}</td>".format(v))
    #curLine = "{}".format(v).ljust(len(longestItem) + 2)
    for x in range(1, numDays.days + 1):
      for c, v2 in calendarDays.items():
        if datetime.strptime(c, "%Y-%m-%d").day == x and v in v2:
          w.write("<td class=\"active\">{}</td>".format(" "))
          #curLine = curLine + "X"
        elif datetime.strptime(c, "%Y-%m-%d").day == x and v not in v2:
          w.write("<td>{}</td>".format(" "))
          #curLine = curLine + " "
    #print (curLine)
    w.write("</tr>")
  w.write("</tbody>")
  w.write("</table>")
  w.write("</body></html>")

#print (max(aspects, key=len))

#   for a, v in aspectsDict.items():
#     w.write("{}:\n".format(aspectsDict[a].Name()))
#     for t in aspectsDict[a].timestamps:
#       w.write("  {}\n".format(t.TimestampRange()))
#     w.write("\n")

# with open("monthlyout\\{:04d}-{:02d}-monthly-sign-retrograde-changes.txt".format(processDateTime.year, processDateTime.month), "r", encoding="utf-8") as r:
#   for b, v in bodiesDict.items():
#     w.write("{}:\n".format(bodiesDict[b].Name()))
#     for t in bodiesDict[b].timestamps:
#       outline = t.AllChanges()
#       if outline != "":
#         w.write("{}\n".format(outline))
#       else:
#         w.write("- No direction or sign changes.\n\n")