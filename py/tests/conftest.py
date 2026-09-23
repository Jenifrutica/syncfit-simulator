import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from syncfit_core import FatigueModel, train_default_model  # noqa: E402

SESSION_ID = "3f1b2c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"


@pytest.fixture(scope="session")
def model() -> FatigueModel:
    return train_default_model(n_samples=600, seed=42)
