import os, pytest

import grg_mpdata

class Test4Bus:
    def setup_method(self, _):
        """Parse a real network file"""
        self.case = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case4_000.m')

    def test_001(self):
        assert len(self.case.bus) == 4

    def test_002(self):
        assert len(self.case.branch) == 4

    def test_003(self):
        path = 'tmp.mp'
        grg_mpdata.io.write_mp_case_file(path, self.case)
        os.remove(path)


class Test6Bus:
    def setup_method(self, _):
        """Parse a real network file"""
        self.case = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case6_000.m')
        #self.case = parse_mp_case(os.path.dirname(os.path.realpath(__file__))+'/data/case6ww.m')

    def test_001(self):
        assert len(self.case.bus) == 6

    def test_002(self):
        assert len(self.case.branch) == 11



