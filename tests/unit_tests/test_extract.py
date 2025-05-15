# The following function was generated with the assistance of ChatGPT.
import os
from unittest.mock import MagicMock
import pytest
import etl.extract.extract as extct


@pytest.fixture(autouse=True)
def isolate_output_dir(tmp_path, monkeypatch):
    # sets a dummy output directory for the test
    monkeypatch.setattr(extct, "output_dir", str(tmp_path))
    monkeypatch.setattr(extct, "csv_filename", "games_march2025_full.csv")
    monkeypatch.setattr(extct, "csv_path", str(
        tmp_path / "games_march2025_full.csv"
        ))
    return tmp_path


def test_extract_calls_kaggle_api_on_success(tmp_path, monkeypatch):
    # Ensure the file "exists" after download
    monkeypatch.setattr(os.path, "exists", lambda path: True)

    # Wololo the kaggle API
    fake_api = MagicMock()
    fake_api.authenticate.return_value = None
    fake_api.dataset_download_file.return_value = None
    monkeypatch.setattr(extct, "KaggleApi", lambda: fake_api)

    # Call under test
    extct.extract_steam_data()

    # assert calls
    fake_api.authenticate.assert_called_once()
    fake_api.dataset_download_file.assert_called_once_with(
        dataset=extct.dataset_id,
        file_name=extct.csv_filename,
        path=extct.output_dir,
        force=True,
    )


def test_extract_prints_error_when_file_missing(monkeypatch, capsys):
    # check that the file does not exist
    monkeypatch.setattr(os.path, "exists", lambda path: False)

    # WOlolo the kaggle API
    fake_api = MagicMock()
    fake_api.authenticate.return_value = None
    fake_api.dataset_download_file.return_value = None
    monkeypatch.setattr(extct, "KaggleApi", lambda: fake_api)

    # run the function
    extct.extract_steam_data()

    # get the output and assert
    # that the error message is printed
    out = capsys.readouterr().out
    assert "Error during data extraction:" in out
    assert "CSV file not found" in out
