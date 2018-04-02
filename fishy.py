#!/usr/bin/python3

import re, sys, random

from fishes import rectangle_with_fish

#def expandtab(line):
#    ret=""
#    last=0
#    for m in re.finditer('\t', line):
#        ret+=line[last:m.start()]
#        ret+=" "*(8 - len(ret)%8)
#        last=m.end()
#    return ret + line[last:]

def debug(*args):
    pass
    #print(*args, file=sys.stderr)

def contracttab(line):
    ret=""
    line = line.rstrip(" ")
    for x in range(0, len(line), 8):
        chunk=line[x:x+8]
        chunk = re.sub(" {2,}$", "\t", chunk)
        ret+=chunk
    return ret

def expandrewrap(iterable, linelength):
    for line in iterable:
        expanded = line.expandtabs()
        for x in range(0, len(line), linelength):
            yield expanded[x:x+linelength]

class BlankRectangle:
    def __init__(self, start, end, linestart, lineend = None):
        self.start = start
        self.end = end
        self.linestart = linestart
        self.lineend = lineend if lineend is not None else linestart
    def covered_by(self, start, end):
        return start <= self.start and self.end <= end
    def intersected_by(self, start, end):
        #   -----------
        #       ----
        # or
        #  -------
        #     --------
        return start <= self.end and self.start <= end
        #return not(start > self.end or end < self.start)
    def nextlineok(self):
        self.lineend += 1
    def nextlinerestrict(self, start, end):
        return BlankRectangle(max(self.start, start), min(self.end, end),
                              self.linestart, self.lineend + 1)
    def values_of_interest(self):
        return (self.start, self.end)
    def __eq__(self, o):
        return self.values_of_interest() == o.values_of_interest()
    def __hash__(self):
        return hash(self.values_of_interest())
    def score(self):
        return (self.lineend - self.linestart)**2 * (self.end-self.start)
    def fill_with_fish(self, initial = None):
        width = self.end - self.start + 1
        height = self.lineend - self.linestart + 1
        return rectangle_with_fish(width, height, 1, initial = initial)
    def __repr__(self):
        return "BlankRectangle(%s,%s,%s,%s)"%(self.start, self.end,
                                              self.linestart, self.lineend)


LINELENGTH=80
MINWIDTH=5
def get_ranges_from_line(line):
    for m in re.finditer(" {"+str(MINWIDTH)+",}", line):
        yield (m.start(), m.end())
    if len(line) < LINELENGTH - MINWIDTH:
        yield (len(line), LINELENGTH - 1)

class TextWindow:
    def __init__(self):
        self.lines = []
        self.start = 0
    def append(self, line):
        self.lines.append(line)
    def prune(self, start_at_line = None):
        if start_at_line is None:
            start_at_line = self.start + len(self.lines)
        debug("current start:", self.start, "line count:", len(self.lines),
                "next start:", start_at_line)

        to_remove = start_at_line - self.start
        assert to_remove >= 0 and to_remove <= len(self.lines)
        for line in self.lines[:to_remove]:
            print(contracttab(line))
        self.lines = self.lines[to_remove:]
        self.start = start_at_line
    def get_range(self, start, end):
        return self.lines[start - self.start : end - self.start]
    def insert(self, art, at_line, at_pos):
        start_at = at_line - self.start
        assert start_at >= 0
        width = len(art[0])
        debug( #"\tlines:", "\n" + "|\n".join(self.lines) + '|',
                "\tart:","\n"+"|\n".join(art)+"|",
                "\nstartat", self.start)
        for y in range(start_at, start_at + len(art)):
            old = self.lines[y].ljust(at_pos, " ")
            self.lines[y] = (old[:at_pos] + art[y - start_at]
                             + old[at_pos + width:])
        debug("\tnew lines:", "\n" + "|\n".join(self.lines)+"|\n")

if __name__ == "__main__":
    last_rectangles=set()

    text=TextWindow()

    def insert_fishes_into_blank(blank, text):
        debug("handling", blank)
        width = blank.end+1-blank.start
        initial = [x[blank.start:blank.end+1].ljust(width, " ")
                   for x in text.get_range(blank.linestart, blank.lineend + 1)]
        debug("\ninitial before art:", "\n" + "|\n".join(initial)+'|')
        fish = blank.fill_with_fish(initial)
        text.insert(fish, blank.linestart, blank.start)

    for lineno, line in enumerate(expandrewrap(sys.stdin, LINELENGTH)):
        debug("line(",lineno,"): ", repr(line))
        line=line.rstrip('\n')
        text.append(line)
        new_rectangles = set()
        collided_rectangles = set()

        #ranges = []
        #for m in re.finditer(" {"+str(MINWIDTH)+",}", line):
        #    ranges.append((m.start(), m.end()))
        #if len(line) < LINELENGTH - MINWIDTH:
        #    ranges.append((len(line), LINELENGTH-1))

        for start, end in get_ranges_from_line(line):
            known = False
            for old_r in last_rectangles:
                if old_r.intersected_by(start, end):
                    if old_r.start == start and old_r.end == end:
                        known = True
                    if old_r.covered_by(start, end):
                        old_r.nextlineok()
                        collided_rectangles.add(old_r)
                    else:
                        new_rectangles.add(old_r.nextlinerestrict(start, end))

            if not known:
                new_rectangles.add(BlankRectangle(start, end, lineno))

        expired = last_rectangles - collided_rectangles

        expired_list = list(expired)

        debug("old_rectangles:", repr(last_rectangles))
        debug("collided:", repr(collided_rectangles))
        debug("expired:", repr(expired_list))
        debug("new_rectangles:", repr(new_rectangles))

        random.shuffle(expired_list)
        while expired_list:
            blank = expired_list.pop()
            insert_fishes_into_blank(blank, text)

        last_rectangles.difference_update(expired)
        last_rectangles.update(new_rectangles)

        min_line = min(last_rectangles, key=lambda rect: rect.linestart,
                       default=None)
        if min_line is not None:
            min_line = min_line.linestart
        debug("pruning line no:", min_line)
        #text.prune(min_line)

    for blank in last_rectangles:
        insert_fishes_into_blank(blank, text)

    text.prune()
