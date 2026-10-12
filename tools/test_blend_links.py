"""Offline tests for the gallery's downloadable Blender file links."""
import tempfile
import unittest
from pathlib import Path

from add_blend_links import add_download_links


class BlendLinksTest(unittest.TestCase):
    def test_only_existing_blends_get_download_links(self):
        with tempfile.TemporaryDirectory() as root:
            results = Path(root)
            folder = results / "timber-waterwheel"
            folder.mkdir()
            (folder / "timber-waterwheel.blend").write_bytes(b"BLENDER")
            gallery = (
                "<html><style>p {color:red}</style>"
                "<code>timber-waterwheel</code>"
                "<code>missing-model</code></html>"
            )
            items = [{"id": "timber-waterwheel"}, {"id": "missing-model"}]
            result, data, count = add_download_links(
                gallery, items, "2rwa/tmp-blender-52", results
            )
            self.assertEqual(count, 1)
            self.assertIn(
                "https://raw.githubusercontent.com/2rwa/tmp-blender-52/main/"
                "results/timber-waterwheel/timber-waterwheel.blend",
                result,
            )
            self.assertEqual(result.count("Download .blend"), 1)
            self.assertEqual(result.count(".blend-download {"), 1)
            self.assertIsNone(data[1]["blend"])
            self.assertIn("timber-waterwheel.blend", data[0]["blend"])
            repeated, _, repeated_count = add_download_links(
                result, items, "2rwa/tmp-blender-52", results
            )
            self.assertEqual(repeated_count, 1)
            self.assertEqual(repeated, result)

    def test_reject_unsafe_experiment_and_repo_names(self):
        page = "<html><style></style></html>"
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                add_download_links(page, [{"id": "../bad"}], "2rwa/repo", Path(root))
            with self.assertRaises(ValueError):
                add_download_links(page, [], "wrong repository", Path(root))


if __name__ == "__main__":
    unittest.main()
