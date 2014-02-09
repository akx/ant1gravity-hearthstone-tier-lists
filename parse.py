from lxml.html import parse
from lxml.etree import tostring
from pprint import pprint
import re, glob, json

max_re = re.compile(r"\(max (\d+)\)", re.I)

scale_values = {
	"Top":		+10,
	"Great":	+8,
	"Good":	+6,
	"Usually Good":	+5,
	"Above Average":	+3,
	"Average":	+1,
	"Below Average":	-3,
	"Usually Bad":	-5,
	"Bad":	-7,
	"Terrible":	-10,
}


def parse_file(fh):
	p = parse(fh).getroot()

	active_tab = tostring(p.cssselect("#sheettabs li.active")[0], method="text")

	values = {}
	scale = None

	for row in p.cssselect("tr"):
		cells = [tostring(c, method="text") for c in row.cssselect("td")]
		while cells and not cells[-1]:
			cells.pop(-1)
		while cells and cells[0] == ".":
			cells.pop(0)

		if not cells:
			continue

		if cells[0] and cells[0] in ("Common", "Rare", "Legendary", "Epic"):
			rank = cells[0]
			scale = [None] + cells[1:]
			#print "Parsing rank", rank, "scale", scale
		elif scale:
			for x, cell in enumerate(cells):
				if cell:
					value = scale[x]
					if value:
						max_val = [None]
						cell = max_re.sub(lambda m:max_val.__setitem__(0,m.group(1)) or "", cell).strip()
						values[cell] = {'rarity': rank, 'value': scale_values[value], 'value_text': value, 'max': max_val[0]}

	return active_tab, values


for fn in glob.glob("input/pub*"):
	with file(fn, "rb") as fh:
		active_tab, values = parse_file(fh)
		name = active_tab.lower().strip()
		
		with file("json/%s.json" % name, "wb") as outfh:
			json.dump(values, outfh, indent=1)
		
		with file("pretty/%s.txt" % name, "wt") as outfh:
			for name, info in sorted(values.iteritems(), key=lambda p:-p[1]["value"]):
				value = info["value"]
				print >>outfh, "%-30s .. %+3d .. %14s|%-14s # %s" % (name, value, "-" * -(value), "#" * (value), info["rarity"])