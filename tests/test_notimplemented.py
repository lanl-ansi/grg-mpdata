'''tests notimplemented brnach of == and != definitions for data structures for code coverage'''

import grg_mpdata

def test_001():
    struct1 = grg_mpdata.struct.Generator(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.GeneratorCost(0, 0, 0, 0, 0)
    assert(not struct1 == struct2)
    assert(not struct2 == struct1)
    assert(struct1 != struct2)
    assert(struct2 != struct1)

def test_002():
    struct1 = grg_mpdata.struct.Branch(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.DCLine(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert(not struct1 == struct2)
    assert(not struct2 == struct1)
    assert(struct1 != struct2)
    assert(struct2 != struct1)

def test_003():
    struct1 = grg_mpdata.struct.Bus(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    struct2 = grg_mpdata.struct.Case()
    assert(not struct1 == struct2)
    assert(not struct2 == struct1)
    assert(struct1 != struct2)
    assert(struct2 != struct1)

