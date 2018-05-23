import os, pytest, grg_mpdata

parser = grg_mpdata.io.build_cli_parser()

def test_001():
    args = parser.parse_args([os.path.dirname(os.path.realpath(__file__))+'/data/correct/case4_000.m'])
    grg_mpdata.io.main(args)

def test_002():
    with pytest.raises(SystemExit):
        args = parser.parse_args([])
        grg_mpdata.io.main(args)
