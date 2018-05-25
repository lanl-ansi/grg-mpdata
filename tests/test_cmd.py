import os, pytest

import grg_mpdata


class TestDiff:
    def setup_method(self, _):
        """Parse a real network file"""
        self.case_1 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case2_000.m')
        self.case_2 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_000.m')
        self.case_3 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_001.m')
        self.case_4 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case4_000.m')
        self.case_5 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case6_000.m')

    def test_001(self):
        count = grg_mpdata.cmd.diff(self.case_1, self.case_2)
        assert(count == 8)

    def test_002(self):
        count = grg_mpdata.cmd.diff(self.case_2, self.case_3)
        assert(count == 0)

    def test_003(self):
        count = grg_mpdata.cmd.diff(self.case_3, self.case_4)
        assert(count == 7)

    def test_004(self):
        count = grg_mpdata.cmd.diff(self.case_4, self.case_5)
        assert(count == 14)

    def test_005(self):
        count = grg_mpdata.cmd.diff(self.case_2, self.case_5)
        assert(count == 14)


class TestEq:
    def setup_method(self, _):
        """Parse a real network file"""
        self.case_1 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case2_000.m')
        self.case_2 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_000.m')
        self.case_3 = grg_mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_001.m')

    def test_001(self):
        equiv = grg_mpdata.cmd.eq(self.case_1, self.case_2)
        assert(not equiv)

    def test_002(self):
        equiv = grg_mpdata.cmd.eq(self.case_2, self.case_3)
        assert(equiv)


class TestCLI:
    def setup_method(self, _):
        """Parse a real network file"""
        self.parser = grg_mpdata.cmd.build_cmd_parser()
        self.case_1_file = os.path.dirname(os.path.realpath(__file__))+'/data/correct/case2_000.m'
        self.case_2_file = os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_000.m'
        self.case_3_file = os.path.dirname(os.path.realpath(__file__))+'/data/correct/case3_001.m'

    def test_diff_001(self):
        args = self.parser.parse_args(['diff', self.case_1_file, self.case_2_file])
        count = grg_mpdata.cmd.main(args)
        assert(count == 8)

    def test_diff_001(self):
        args = self.parser.parse_args(['diff', self.case_2_file, self.case_3_file])
        count = grg_mpdata.cmd.main(args)
        assert(count == 0)

    def test_eq_001(self):
        args = self.parser.parse_args(['eq', self.case_1_file, self.case_2_file])
        equiv = grg_mpdata.cmd.main(args)
        assert(not equiv)

    def test_eq_002(self):
        args = self.parser.parse_args(['eq', self.case_2_file, self.case_3_file])
        equiv = grg_mpdata.cmd.main(args)
        assert(equiv)

