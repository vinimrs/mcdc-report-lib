import pytest
from placar import Placar

def test_conta():
    assert Placar.conta(3, [1,3,3,2,3]) == 3
    assert Placar.conta(5, []) == 0

def test_check_full():
    # full house: 3 of a kind + pair
    assert Placar.checkFull([2,2,2,3,3]) is True
    assert Placar.checkFull([3,3,4,4,4]) is True
    assert Placar.checkFull([1,2,3,4,5]) is False

def test_check_seq_maior():
    assert Placar.checkSeqMaior([1,2,3,4,5]) is True
    assert Placar.checkSeqMaior([2,3,4,5,6]) is True
    assert Placar.checkSeqMaior([1,2,2,4,5]) is False

def test_check_quadra():
    assert Placar.checkQuadra([6,6,6,6,2]) is True
    assert Placar.checkQuadra([1,2,3,4,5]) is False

def test_check_quina():
    assert Placar.checkQuina([4,4,4,4,4]) is True
    assert Placar.checkQuina([4,4,4,4,5]) is False

def test_add_and_scores():
    p = Placar()
    # test numeric slot (Ones)
    p.add(1, [1,2,1,1,3])  # three 1's => 3 * 1 = 3
    assert p.getTaken(0) is True
    assert p.getScore(0) == 3
    assert p.getName(0) == "Ones"
    # test Full House
    p.add(7, [2,2,2,3,3])
    assert p.getScore(6) == 15
    # test Sequence
    p.add(8, [2,3,4,5,6])
    assert p.getScore(7) == 20
    # test Four of a Kind
    p.add(9, [5,5,5,5,1])
    assert p.getScore(8) == 30
    # test General (Quina)
    p.add(10, [6,6,6,6,6])
    assert p.getScore(9) == 40
    # total score
    expected = 3 + 15 + 20 + 30 + 40
    assert p.getScore() == expected

# def test_add_invalid_and_taken():
#     p = Placar()
#     with pytest.raises(IndexError):
#         p.add(0, [1,1,1,1,1])
#     with pytest.raises(IndexError):
#         p.add(11, [1,1,1,1,1])
#     # occupy a slot and attempt to reuse
#     p2 = Placar()
#     p2.add(1, [1,1,1,1,1])
#     with pytest.raises(ValueError):
#         p2.add(1, [1,1,1,1,1])

def test_str_placeholder():
    p = Placar()
    s = str(p)
    # untaken slots should show "(1)" and "(10)" placeholders
    assert "(1) " in s