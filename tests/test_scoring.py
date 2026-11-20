from mini_swe_bench.report import calculate_reward


def test_reward_with_all_tests_passed():
    results = {
        "fail_to_pass": [{"status": "passed"}, {"status": "passed"}],
        "pass_to_pass": [{"status": "passed"}, {"status": "passed"}],
    }

    reward = calculate_reward(results)

    assert reward["reward"] == 100
    assert reward["fix_rate"] == 1.0
    assert reward["regression_rate"] == 1.0


def test_reward_with_only_half_bug_fixes():
    results = {
        "fail_to_pass": [{"status": "passed"}, {"status": "failed"}],
        "pass_to_pass": [{"status": "passed"}],
    }

    reward = calculate_reward(results)

    assert reward["reward"] == 65.0
    assert reward["fix_rate"] == 0.5
    assert reward["regression_rate"] == 1.0


def test_reward_is_zero_when_no_bug_tests_exist():
    results = {
        "fail_to_pass": [],
        "pass_to_pass": [{"status": "passed"}],
    }

    reward = calculate_reward(results)

    assert reward["reward"] == 30.0
    assert reward["fix_rate"] == 0.0
