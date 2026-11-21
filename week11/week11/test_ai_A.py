import pytest

from load_scores import load_scores


def test_valid_scores_are_kept_and_normalized(tmp_path):
    path = tmp_path / "scores.csv"
    path.write_text(
        "name,score\n"
        " Alice , 0 \n"
        "Bob,100\n"
        "Alice,75\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    assert kept == [("Alice", 0), ("Bob", 100), ("Alice", 75)]
    assert skipped == []


def test_invalid_rows_are_skipped_with_line_number_source_and_reason(tmp_path):
    path = tmp_path / "scores.csv"
    path.write_text(
        "name,score\n"
        " ,90\n"
        "Alice,\n"
        "Bob,not-a-number\n"
        "Carol,-1\n"
        "Dan,101\n"
        "Eve\n"
        "Frank,80,extra\n"
        "\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, " ,90", "이름이 비어 있음"),
        (3, "Alice,", "점수가 비어 있음"),
        (4, "Bob,not-a-number", "점수가 정수가 아님"),
        (5, "Carol,-1", "점수가 0~100 밖"),
        (6, "Dan,101", "점수가 0~100 밖"),
        (7, "Eve", "열 개수가 2가 아님"),
        (8, "Frank,80,extra", "열 개수가 2가 아님"),
    ]


@pytest.mark.parametrize("contents", ["", "name,score\n"])
def test_empty_file_or_header_only_returns_empty_lists(tmp_path, contents):
    path = tmp_path / "scores.csv"
    path.write_text(contents, encoding="utf-8")

    assert load_scores(path) == ([], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")