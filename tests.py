#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
import unittest
from ascii_art_sprinkler import Rect, BlankFinder, AsciiCanvas

def blank_finder_for(string):
    finder = BlankFinder(80, 1, 999)
    for line in string.split('\n'):
        finder.add_line(line)
    finder.end_of_file()
    return finder

def find_rects(string):
    return list(blank_finder_for(string).drain_fillable_blanks())

def as_art(string):
    assert string[0] == '\n' and string[-1] == '\n'
    return string[1:-1]

class TestFindBlank(unittest.TestCase):
    def test_simple(self):

        self.assertCountEqual(find_rects("\n\n"),
                              [Rect(0, 80, 1, 4)])
        self.assertCountEqual(find_rects("a a a"),
                              [Rect(1, 2, 1, 2),
                               Rect(3, 4, 1, 2),
                               Rect(5, 80, 1, 2)])
        self.assertCountEqual(find_rects("""
0123456789"""),
                              [Rect(0, 80, 1, 2),
                               Rect(10, 80, 1, 3)])

        self.assertCountEqual(find_rects("""
          0123456789"""),
                              [Rect(0, 80, 1, 2),
                               Rect(0, 10, 1, 3),
                               Rect(20, 80, 1, 3)])
        self.assertCountEqual(find_rects("          0123456789\n"),
                              [Rect(0, 10, 1, 3), Rect(20, 80, 1, 3),
                               Rect(0, 80, 2, 3)])

    def test_disjoint(self):
        self.assertCountEqual(find_rects(as_art("""
AAA  AAAAAAA
  AAAAAAAAAA
""")),
                              [Rect(3, 5, 1, 2), Rect(0, 2, 2, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
  AAAAAAAAAA
AAA  AAAAAAA
""")),
                              [Rect(0, 2, 1, 2), Rect(3, 5, 2, 3),
                               Rect(12, 80, 1, 3)])

    def test_enlarge(self):
        self.assertCountEqual(find_rects(as_art("""
AAAA   AAAAA
AA       AAA
""")),
                              [Rect(4, 7, 1, 3), Rect(2, 9, 2, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AA     AAAAA
AA       AAA
""")),
                              [Rect(2, 7, 1, 3), Rect(2, 9, 2, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AA       AAA
AA       AAA
""")),
                              [Rect(2, 9, 1, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AAAA     AAA
AA       AAA
""")),
                              [Rect(4, 9, 1, 3), Rect(2, 9, 2, 3),
                               Rect(12, 80, 1, 3)])
    def test_narrow(self):
        self.assertCountEqual(find_rects(as_art("""
AA     AAAAA
     AAAAAAA
""")),
                              [Rect(2, 7, 1, 2),
                               Rect(2, 5, 1, 3),
                               Rect(0, 5, 2, 3),
                               Rect(12, 80, 1, 3)])

        self.assertCountEqual(find_rects(as_art("""
AA     AAAAA
AAAA     AAA
""")),
                              [Rect(2, 7, 1, 2),
                               Rect(4, 7, 1, 3),
                               Rect(4, 9, 2, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AA       AAA
AA     AAAAA
""")),
                              [Rect(2, 9, 1, 2),
                               Rect(2, 7, 1, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AA       AAA
AAAA   AAAAA
""")),
                              [Rect(2, 9, 1, 2),
                               Rect(4, 7, 1, 3),
                               Rect(12, 80, 1, 3)])
        self.assertCountEqual(find_rects(as_art("""
AA       AAA
AAAA     AAA
""")),
                              [Rect(2, 9, 1, 2),
                               Rect(4, 9, 1, 3),
                               Rect(12, 80, 1, 3)])

    def test_typicaly(self):
        input_text = as_art("""

Hi !

This is a test of the blank finder.

Don't pay attention !
""")
        end_of_lines = [
                Rect(0, 80, 1, 2),
                Rect(4, 80, 1, 4),
                Rect(0, 80, 3, 4),
                Rect(35, 80, 1, 7),
                Rect(0, 80, 5, 6),
                Rect(21, 80, 5, 7)
        ]
        spaces = [
                Rect(2, 3, 1, 4), # Hi !
                Rect(4, 5, 1, 6), # This is
                Rect(7, 8, 1, 6), # is a
                Rect(9, 10, 1, 7), # a test / pay attention
                Rect(14, 15, 1, 6), # test of
                Rect(17, 18, 1, 6), # of the
                Rect(21, 22, 1, 7), # the blank
                Rect(27, 28, 1, 7), # blank finder.

                Rect(5, 6, 5, 7), # Dont' pay
                Rect(19, 20, 5, 7) # attention !
        ]
        self.maxDiff = None
        self.assertCountEqual(find_rects(input_text), end_of_lines + spaces)


class TestFillBlank(unittest.TestCase):
    def fill_every_blank(self, string):
        rects = find_rects(string)
        for rect in rects:
            finder = blank_finder_for(string)
            filling = AsciiCanvas.from_text("w")
            filling.increase_size(rect.width(), rect.height())
            self.assertTrue(finder.try_fill_blank(rect, filling),
                            "Cannot fill {}".format(rect))

    def test_fill_simple(self):
        self.fill_every_blank(as_art("""
1234567890

          0123456789

"""))

    def test_fill_disjont(self):
        self.fill_every_blank(as_art("""
AAAAAAAAAAAAAAAA
          AAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAA
"""))

    def test_fill_enlarge(self):
        self.fill_every_blank(as_art("""
AAAA    AAAAAAAA   AAAAAAAA AAAA    AAAAAAA
AA        AAAAAA     AAAA   AAAA    AAAAAAA
"""))

    def test_fill_narrow(self):
        self.fill_every_blank(as_art("""
AA        AAAAAA     AAAA   AAAA    AAAAAAA
AAAA    AAAAAAAA   AAAAAAAA AAAA    AAAAAAA
"""))

    def test_fill_typical(self):
        self.fill_every_blank(as_art("""

Hi !

This is a test of the blank finder.

Don't pay attention !
"""))

if __name__ == '__main__':
    unittest.main()
