from pathlib import Path


def test_expected_stage_directories_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "ingestion").is_dir()
    assert (root / "src" / "processing").is_dir()
    assert (root / "src" / "analytics").is_dir()
