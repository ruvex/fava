from datetime import date
from datetime import datetime as dt

import pytest
# from unittest import mock

from fava.util.date import (parse_date, get_next_interval, interval_tuples,
                            number_of_days_in_period)


@pytest.mark.parametrize('input_date_string,interval,expect', [
    ('2016-01-01', 'day', '2016-01-02'),
    ('2016-01-01', 'week', '2016-01-04'),
    ('2016-01-01', 'month', '2016-02-01'),
    ('2016-01-01', 'quarter', '2016-04-01'),
    ('2016-01-01', 'year', '2017-01-01'),

    ('2016-12-31', 'day', '2017-01-01'),
    ('2016-12-31', 'week', '2017-01-02'),
    ('2016-12-31', 'month', '2017-01-01'),
    ('2016-12-31', 'quarter', '2017-01-01'),
    ('2016-12-31', 'year', '2017-01-01'),
])
def test_get_next_interval(input_date_string, interval, expect):
    """Test for get_next_interval function."""
    input_date = dt.strptime(input_date_string, '%Y-%m-%d')
    get = get_next_interval(input_date, interval)
    assert get.strftime('%Y-%m-%d') == expect


def test_get_next_interval_exception():
    with pytest.raises(NotImplementedError):
        get_next_interval(date(2016, 4, 18), 'decade')


def test_interval_tuples():
    assert interval_tuples(date(2014, 3, 5), date(2014, 5, 5), 'month') == [
        (date(2014, 3, 5), date(2014, 4, 1)),
        (date(2014, 4, 1), date(2014, 5, 1)),
        (date(2014, 5, 1), date(2014, 6, 1)),
    ]
    assert interval_tuples(date(2014, 3, 5), date(2014, 5, 5), 'year') == [
        (date(2014, 3, 5), date(2015, 1, 1)),
    ]
    assert interval_tuples(date(2014, 1, 1), date(2015, 1, 1), 'year') == [
        (date(2014, 1, 1), date(2015, 1, 1)),
    ]
    assert interval_tuples(None, None, None) == []


def to_date(string):
    """to_date convert a string in %Y-%m-%d into a datetime.date object.

    Return None if string is None.
    """
    if string is None:
        return None
    return dt.strptime(string, '%Y-%m-%d').date()


@pytest.mark.parametrize("expect_start,expect_end,text", [
    (None, None, '    '),
    ('2000-01-01', '2001-01-01', '   2000   '),
    ('2010-10-01', '2010-11-01', '2010-10'),
    ('2000-01-03', '2000-01-04', '2000-01-03'),
    ('2015-01-05', '2015-01-12', '2015-W01'),
    ('2015-04-01', '2015-07-01', '2015-Q2'),
    ('2014-01-01', '2016-01-01', '2014 to 2015'),
    ('2014-01-01', '2016-01-01', '2014-2015'),
    ('2011-10-01', '2016-01-01', '2011-10 - 2015'),
])
def test_parse_date(expect_start, expect_end, text):
    """Test for parse_date() function."""
    start, end = to_date(expect_start), to_date(expect_end)
    assert parse_date(text) == (start, end)


# def test_parse_date_relative(pseudo_today, expect_start, expect_end, text):
#     """Test for parse_date() function."""
#     # Mock the imported datetime.date in fava.util.date module
#     # Ref:
#     # http://www.voidspace.org.uk/python/mock/examples.html#partial-mocking
#     with mock.patch('fava.util.date.datetime.date') as mock_date:
#         mock_date.today.return_value = to_date(pseudo_today) or date.today()
#         mock_date.side_effect = date
#         got = parse_date(text)
#     start, end = to_date(expect_start), to_date(expect_end)
#     assert got == (start, end), "parse_date(%s) == %s @ %s, want (%s, %s)" % (
#         text, got, pseudo_today, start, end)


def test_number_of_days_in_period_daily():
    assert number_of_days_in_period('daily', dt(2016, 5, 1)) == 1
    assert number_of_days_in_period('daily', dt(2016, 5, 2)) == 1
    assert number_of_days_in_period('daily', dt(2016, 5, 31)) == 1


def test_number_of_days_in_period_weekly():
    assert number_of_days_in_period('weekly', dt(2016, 5, 1)) == 7
    assert number_of_days_in_period('weekly', dt(2016, 5, 2)) == 7
    assert number_of_days_in_period('weekly', dt(2016, 5, 31)) == 7


def test_number_of_days_in_period_monthly():
    assert number_of_days_in_period('monthly', dt(2016, 5, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 5, 2)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 5, 31)) == 31

    assert number_of_days_in_period('monthly', dt(2016, 6, 1)) == 30
    assert number_of_days_in_period('monthly', dt(2016, 6, 15)) == 30
    assert number_of_days_in_period('monthly', dt(2016, 6, 30)) == 30

    assert number_of_days_in_period('monthly', dt(2016, 7, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 7, 15)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 7, 31)) == 31

    assert number_of_days_in_period('monthly', dt(2016, 1, 1)) == 31
    assert number_of_days_in_period('monthly', dt(2016, 2, 1)) == 29
    assert number_of_days_in_period('monthly', dt(2016, 3, 31)) == 31


def test_number_of_days_in_period_quarterly():
    # 2016 = leap year
    assert number_of_days_in_period('quarterly', dt(2016, 2, 1)) == 91
    assert number_of_days_in_period('quarterly', dt(2016, 5, 30)) == 91
    assert number_of_days_in_period('quarterly', dt(2016, 8, 15)) == 92
    assert number_of_days_in_period('quarterly', dt(2016, 11, 15)) == 92

    # 2017 = not a leap year
    assert number_of_days_in_period('quarterly', dt(2017, 2, 1)) == 90
    assert number_of_days_in_period('quarterly', dt(2017, 5, 30)) == 91
    assert number_of_days_in_period('quarterly', dt(2017, 8, 15)) == 92
    assert number_of_days_in_period('quarterly', dt(2017, 11, 15)) == 92


def test_number_of_days_in_period_yearly():
    assert number_of_days_in_period('yearly', dt(2011, 2, 1)) == 365
    assert number_of_days_in_period('yearly', dt(2015, 5, 30)) == 365
    assert number_of_days_in_period('yearly', dt(2016, 8, 15)) == 366


def test_number_of_days_in_period_exception():
    with pytest.raises(Exception):
        number_of_days_in_period('test', dt(2011, 2, 1)) == 365
