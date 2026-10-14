"""Regression checks for long thin Japanese utensils, normal assets, and bad previews."""
import unittest
from validate import validate_silhouette

class PreviewSilhouetteTests(unittest.TestCase):
 def test_vertical_fude_38x311(self):
  self.assertEqual(validate_silhouette((231,27,269,338),700),(38,311))
 def test_horizontal_shinobue_326x28(self):
  self.assertEqual(validate_silhouette((87,303,413,331),900),(326,28))
 def test_horizontal_chashaku_326x38(self):
  self.assertEqual(validate_silhouette((87,292,413,330),1100),(326,38))
 def test_standard_bowl(self):
  self.assertEqual(validate_silhouette((100,60,403,352),16000),(303,292))
 def test_blank(self):
  with self.assertRaises(AssertionError):validate_silhouette(None,0)
 def test_pixel_count(self):
  with self.assertRaises(AssertionError):validate_silhouette((87,303,413,331),120)
 def test_microscopic_asset(self):
  with self.assertRaises(AssertionError):validate_silhouette((200,200,260,230),1200)
 def test_edge_on(self):
  with self.assertRaises(AssertionError):validate_silhouette((100,20,420,27),1500)

if __name__=="__main__":unittest.main()
