import pytest, warnings

import grg_mpdata

from test_common import correct_files
from test_common import warning_files


#@pytest.mark.filterwarnings('error')
@pytest.mark.parametrize('input_data', correct_files)
def test_001(input_data):
    case = grg_mpdata.io.parse_mp_case_file(input_data)
    mp_data = case.to_matpower()
    case_2 = grg_mpdata.io.parse_mp_case_str(mp_data)
    assert case == case_2 # checks full data structure
    assert not case != case_2
    assert str(case) == str(case_2) # checks string representation of data structure

    diff_count = grg_mpdata.cmd.diff(case, case_2)
    assert diff_count <= 0


#@pytest.mark.filterwarnings('default')
@pytest.mark.parametrize('input_data', warning_files)
def test_002(input_data):
    case = grg_mpdata.io.parse_mp_case_file(input_data)
    mp_data = case.to_matpower()
    case_2 = grg_mpdata.io.parse_mp_case_str(mp_data)
    assert case == case_2 # checks full data structure
    assert not case != case_2
    assert str(case) == str(case_2) # checks string representation of data structure

    diff_count = grg_mpdata.cmd.diff(case, case_2)
    assert diff_count <= 0
