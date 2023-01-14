import pytest
from pycta.analysis import Analysis

@pytest.fixture
def analysis(prices):
    # we need only one time series
    nav = prices["B"]
    return Analysis(nav)


def test_std(analysis):
    assert analysis.std["2013-02-03"] == pytest.approx(0.004341629905864831)


def test_monthlytable(analysis):
    assert analysis.monthlytable["STDev"].loc[2015] == "18.89%"


def test_performance(analysis):
    print(analysis.performance)
    assert analysis.performance["Max Drawdown"] == "14.58"
