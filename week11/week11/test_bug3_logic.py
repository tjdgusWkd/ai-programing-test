from bug3_logic import count_pass, find_max


def test_find_max_includes_the_last_score():
    assert find_max([70, 85, 60, 95]) == 95


def test_count_pass_includes_scores_equal_to_cutoff():
    assert count_pass([70, 85, 60, 95]) == 4