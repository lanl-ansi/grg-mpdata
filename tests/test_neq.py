'''tests of not equal definitions on data structures for code coverage'''

import grg_mpdata

def test_001():
    struct1 = grg_mpdata.struct.Generator(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.Generator(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert(not struct1 != struct2)

def test_002():
    struct1 = grg_mpdata.struct.GeneratorCost(0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.GeneratorCost(0, 0, 0, 0, 0)
    assert(not struct1 != struct2)

def test_003():
    struct1 = grg_mpdata.struct.Bus(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.Bus(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert(not struct1 != struct2)

def test_004():
    struct1 = grg_mpdata.struct.Branch(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.Branch(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert(not struct1 != struct2)

def test_005():
    struct1 = grg_mpdata.struct.DCLine(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.DCLine(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert(not struct1 != struct2)