import unittest

from scripts.real.download_study_datasets import (
    DATASET_DIRS,
    DATASET_REPO_ID,
    REQUIRED_FEATURES,
    validate_dataset_metadata,
)


class StudyDatasetDownloadTests(unittest.TestCase):
    def test_all_conditions_use_the_projects_single_dataset_repo(self):
        self.assertEqual(DATASET_REPO_ID, "giaobo/so101-smovla")
        self.assertEqual(
            DATASET_DIRS,
            {
                "clean": "cube-pickup-clean",
                "randomized": "cube-pickup-randomized",
                "recovery": "cube-pickup-recovery",
                "color": "cube-pickup-color",
            },
        )

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
