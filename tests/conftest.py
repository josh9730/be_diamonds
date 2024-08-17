import pandas as pd
import pytest


@pytest.fixture
def fixture_audit_df():
    return pd.read_csv('tests/fixture.csv')
