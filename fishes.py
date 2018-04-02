
# -*- encoding: utf-8 -*-
fishes=[
"""
 _///_
/o    \/
> ))_./\\
   <
""","""
     .-""L_
;`, /   ( o\\
\  ;    `, /
;_/"`.__.-"
""",
"""
 _J""-.
/o )   \ ,';
\ ,'    ;  /
 "-.__.'"\_;
""",
"""
 .-=-.  ,
(     ><
 `-=-'  `
""",
"""
   _.-=-._     .-,
 .'       "-.,' /
(          _.  <
 `=.____.="  `._\\
""",
"""
<><
 <><
<><
""",
"""
 __
/o \/
\__/\\
""","""
  _
 /. \ /|
(_   X |
 \_V/ \|
""","""
><((">
""","""
><(((*>
""","""
|><'>
""","""
|><((o>
""","""
  _///_ //
<`)=  _<<
   \\\\\\  \\\\
""","""
  \\
  /\\
>=)'>
  \/
  /
""","""
  /
 /--\\
<o)  =>
 \--/
  \\
""","""
 /,
<')=<
 \`
""","""
  ,/..
<')   `=<
 ``\```
""","""
 __
<'_><|
 `
""","""
>°))))))))><<
"""
]

def adjusted_splitted(art_as_string):
    s = art_as_string.strip('\n').split('\n')
    width = max(len(x) for x in s)
    return [x.ljust(width, " ") for x in s]

fishes = [adjusted_splitted(fish) for fish in fishes]

inversion={"/":"\\", "\\":"/", "<":">",">":"<", "'":"'", "|":"|", "=":"=",
        ".":".", ")":"(", "(":")", "o":"o","-":"-", "_":"_", '"':'"', ";":";",
        "V":"V","X":"X","*":"*", " ":" ","°":"°"}

more_fishes = []
for art in fishes:
    try:
        more_fishes.append(["".join(inversion[c] for c in line[::-1])
                            for line in art])
    except:
        pass
fishes.extend(more_fishes)

fishes.sort(key=lambda art: len(art) * len(art[0]), reverse=True)

import random, sys

def test_clearance(art, x_start, x_end, y_start, y_end):
    width = len(art[0])
    height = len(art)
    if x_start < 0 or y_start < 0 or x_end >= width or y_end >= height:
        return False
    for y in range(y_start, y_end + 1):
        if art[y][x_start:x_end+1] != " "*(x_end - x_start + 1):
            return False
    return True

def debug(*args):
    pass#print(*args, file=sys.stderr)

def rectangle_with_fish(width, height, margin, initial=None, max_tries = 13):
#    width = self.end - self.start + 1
#    height = self.lineend - self.linestart + 1
    if initial is None:
        ret = [" "*width] * height
    else:
        debug("initial is not None")
        ret = [x.ljust(width, " ") for x in initial]
        debug("initialized to", repr(ret))

    max_fish = len(fishes) - 1
    while max_tries:
        max_tries -= 1
        try:
            fish_index = random.randint(0, max_fish)
            fish = fishes[fish_index]
        except:
            debug("max_fish: ", repr(max_fish))
            raise
        w_fish = len(fish[0])
        h_fish = len(fish)
        if w_fish + 2 * margin >= width or h_fish + 2 * margin>= height:
            max_fish = fish_index
            continue
        x_shift = random.randint(margin, width - w_fish - margin)
        y_shift = random.randint(margin, height - h_fish - margin)
        x_start = max(x_shift - margin, 0)
        x_end = min(x_shift + w_fish + margin, width)
        y_start = max(y_shift - margin, 0)
        y_end = min(y_shift + h_fish + margin, height)
        if not test_clearance(ret, x_start, x_end, y_start, y_end):
            continue
        for y in range(y_shift, y_shift + h_fish):
            try:
                ret[y] = (ret[y][:x_shift]
                            + fish[y - y_shift]
                            + ret[y][x_shift+w_fish:])
            except:
                debug("x: ", x_start, x_end, "y: ", y_start, y_end)
                debug("ret[y]:", repr(ret[y]), len(ret[y]))
                raise
    return ret

