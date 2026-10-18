import json

import pandas as pd
import pytest

from src.cli import main


def test_cli_exports_complete_run_and_does_not_overwrite(tmp_path):
    arguments = ["--days", "1", "--population", "10", "--seed", "7", "--output", str(tmp_path), "--no-plot"]
    assert main(arguments) == 0
    assert main(arguments) == 0
    runs = list(tmp_path.iterdir())
    assert len(runs) == 2
    for run in runs:
        assert {path.name for path in run.iterdir()} == {"metrics.csv", "config.json", "summary.json", "metadata.json"}
        history = pd.read_csv(run / "metrics.csv")
        assert len(history) == 25
        assert history.iloc[-1]["hour"] == 24
        assert json.loads((run / "config.json").read_text())["seed"] == 7
        summary = json.loads((run / "summary.json").read_text())
        assert sum(summary["final_states"].values()) == 10


def test_cli_rejects_invalid_configuration_before_writing(tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["--population", "0", "--output", str(tmp_path)])
    assert error.value.code == 2
    assert list(tmp_path.iterdir()) == []
