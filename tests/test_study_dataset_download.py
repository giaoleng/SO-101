import unittest

from scripts.real.download_study_datasets import (
    DATASETS,
    REQUIRED_FEATURES,
    validate_dataset_metadata,
)


class StudyDatasetDownloadTests(unittest.TestCase):
    def test_only_four_registered_conditions_are_downloadable(self):
        self.assertEqual(set(DATASETS), {"clean", "randomized", "recovery", "color"})
        self.assertFalse(any("density" in repo_id.lower() for repo_id in DATASETS.values()))

    def test_expected_lerobot_schema_is_validated(self):
        metadata = {
            "total_episodes": 50,
            "fps": 30,
            "features": {
                "action": {"shape": [6]},
                "observation.state": {"shape": [6]},
                "observation.images.overhead": {"shape": [480, 640, 3]},
                "observation.images.wrist": {"shape": [480, 640, 3]},
            },
        }
        validate_dataset_metadata(metadata)
        self.assertEqual(len(REQUIRED_FEATURES), 4)

    def test_wrong_episode_count_is_rejected(self):
        metadata = {
            "total_episodes": 49,
            "fps": 30,
            "features": {
                "action": {"shape": [6]},
                "observation.state": {"shape": [6]},
                "observation.images.overhead": {"shape": [480, 640, 3]},
                "observation.images.wrist": {"shape": [480, 640, 3]},
            },
        }
        with self.assertRaises(ValueError):
            validate_dataset_metadata(metadata)


if __name__ == "__main__":
    unittest.main()
