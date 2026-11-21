import pytest

from load_scores import load_scores


def _write_csv(tmp_path, contents):
    path = tmp_path / "scores.csv"
    path.write_text(contents, encoding="utf-8")
    return path


def test_valid_scores_include_boundaries_and_skip_duplicate_name(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "Alice,0\n"
        "Bob,100\n"
        "Alice,85\n",
    )

    kept, skipped = load_scores(path)

    assert kept == [("Alice", 0), ("Bob", 100)]
    assert len(skipped) == 1
    skipped_line = skipped[0]
    assert skipped_line[0] == 4
    assert "중복" in skipped_line[2]


@pytest.mark.parametrize(
    "contents",
    [
        "",
        "Alice,80\n",
        "student,score\nAlice,80\n",
        "name\nAlice,80\n",
        "name,score,extra\nAlice,80\n",
    ],
)
def test_missing_or_invalid_header_stops_processing(tmp_path, contents):
    path = _write_csv(tmp_path, contents)

    with pytest.raises(ValueError):
        load_scores(path)


def test_header_only_file_returns_empty_lists(tmp_path):
    path = _write_csv(tmp_path, "name,score\n")

    assert load_scores(path) == ([], [])


@pytest.mark.parametrize("invalid_row", ["Eve\n", "Frank,70,extra\n"])
def test_wrong_number_of_data_columns_stops_processing(tmp_path, invalid_row):
    path = _write_csv(tmp_path, "name,score\nAlice,90\n" + invalid_row)

    with pytest.raises(ValueError):
        load_scores(path)


def test_invalid_or_empty_data_is_not_included(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "Alice,0\n"
        "Bob,100\n"
        ",70\n"
        "Carol,\n"
        "Dan,not-a-number\n"
        "Eve,-1\n"
        "Frank,101\n"
        "\n"
        "Grace,80\n",
    )

    kept, skipped = load_scores(path)

    assert kept == [("Alice", 0), ("Bob", 100), ("Grace", 80)]
    assert [row[0] for row in skipped] == [4, 5, 6, 7, 8]


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")