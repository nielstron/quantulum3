import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from quantulum3.scripts import train

TOPDIR = os.path.dirname(__file__) or "."


# pylint: disable=no-self-use
class TrainScriptTest(unittest.TestCase):
    train_classifier_path = "quantulum3.scripts.train.train_classifier"

    def setUp(self):
        self.custom_training_data_path = Path(TOPDIR) / "data" / "train.json"

        with (self.custom_training_data_path).open() as f:
            self.custom_training_data = json.load(f)

    @patch(train_classifier_path)
    def test_train_defaults(self, mock_train_classifier):
        train.main([])

        mock_train_classifier.assert_called_once_with(
            store=False,
            lang="en_US",
            training_set=None,
            output_path=None,
        )

    @patch(train_classifier_path)
    def test_train_output_path(self, mock_train_classifier):
        train.main(["-o", "some/path"])

        mock_train_classifier.assert_called_once_with(
            store=True,
            lang="en_US",
            training_set=None,
            output_path="some/path",
        )

    @patch(train_classifier_path)
    def test_train_data(self, mock_train_classifier):
        train.main(["-d", str(self.custom_training_data_path)])

        mock_train_classifier.assert_called_once_with(
            store=False,
            lang=None,
            training_set=self.custom_training_data,
            output_path=None,
        )

    @patch(train_classifier_path, side_effect=ImportError)
    @patch("quantulum3.scripts.train._LOGGER.error")
    def test_train_data_missing_classifier_deps(
        self, mock_train_classifier, mock_logger_error
    ):
        train.main(["-d", str(self.custom_training_data_path)])

        mock_train_classifier.assert_called_once()
        mock_logger_error.assert_called_once()
