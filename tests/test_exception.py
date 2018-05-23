import pytest

import grg_mpdata

from test_common import incorrect_files

@pytest.mark.parametrize('input_data', incorrect_files)
def test_001(input_data):
    with pytest.raises(grg_mpdata.exception.MPDataException):
        case = grg_mpdata.io.parse_mp_case_file(input_data)
