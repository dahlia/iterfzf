import unittest
import iterfzf

flavors = [
    "Chocolate", "Chocolate Chip", "Vanilla", "Strawberry", "Blueberry",
    "Rocky Road"
]


class IterFzfTest(unittest.TestCase):

    def test_no_query(self):
        choice = iterfzf.iterfzf(flavors, executable="fzf")
        self.assertEqual("Chocolate", choice)

    def test_supports_color_kwarg(self):
        choice = iterfzf.iterfzf(
            flavors,
            executable="fzf",
            color={
                "fg": "#d0d0d0",
                "bg": "#121212",
                "hl": "#5f87af",
                "fg+": "#d0d0d0",
                "bg+": "#262626",
                "hl+": "#5fd7ff",
                "info": "#afaf87",
                "prompt": "#d7005f",
                "pointer": "#af5fff",
                "marker": "#87ff00",
                "spinner": "#af5fff",
                "header": "#87afaf",
            }
        )
        self.assertEqual("Chocolate", choice)

    def test_select_one(self):
        choice = iterfzf.iterfzf(
            flavors, query="Vani", __extra__=["-1"], executable="fzf"
        )
        self.assertEqual("Vanilla", choice)

    def test_select_one_ambiguous(self):
        choice = iterfzf.iterfzf(
            flavors, query="Choc", __extra__=["-1"], executable="fzf"
        )
        self.assertTrue(choice.rfind('Chocolate') == 0)
