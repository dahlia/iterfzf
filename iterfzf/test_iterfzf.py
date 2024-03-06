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
