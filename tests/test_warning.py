import pytest, warnings

import grg_mpdata

from test_common import warning_files

@pytest.mark.parametrize('input_data', warning_files)
def test_001(input_data):
    with pytest.warns(grg_mpdata.exception.MPDataWarning):
        case = grg_mpdata.io.parse_mp_case_file(input_data)
