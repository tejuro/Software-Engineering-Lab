
import pytest

from house_painting_quote import painting_quote, paint_litres, crew_days


# Tests for painting_quote()

def test_interior_distemper():
    assert painting_quote("distemper", 100, 1, False) == 5000


def test_interior_emulsion():
    assert painting_quote("emulsion", 300, 1, False) == 6000


def test_exterior_enamel():
    assert painting_quote("enamel", 500, 2, True) == 32500


def test_unknown_paint():
    with pytest.raises(ValueError, match="unknown paint"):
        painting_quote("unknown", 100, 1, False)


def test_invalid_area():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 0, 1, False)


def test_invalid_coats():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 100, 0, False)


def test_exterior_distemper_rejected():
    with pytest.raises(ValueError, match="distemper is for interiors only"):
        painting_quote("distemper", 100, 1, True)


def test_large_area_discount():
    assert painting_quote("emulsion", 2001, 1, False) == 36018


# Tests for paint_litres()

def test_smooth_litres():
    assert paint_litres(200, 1, "smooth") == 2


def test_rough_litres():
    assert paint_litres(120, 1, "rough") == 2


def test_unknown_surface():
    with pytest.raises(ValueError, match="unknown surface"):
        paint_litres(100, 1, "unknown")


def test_litres_round_up():
    assert paint_litres(101, 1, "smooth") == 2


# Tests for crew_days()

def test_crew_days_exact():
    assert crew_days(800, 2, False) == 1


def test_crew_days_round_up():
    assert crew_days(801, 2, False) == 2


def test_crew_days_wallpaper_removal():
    assert crew_days(400, 1, True) == 3


def test_invalid_painter_count():
    with pytest.raises(ValueError, match="need at least one painter"):
        crew_days(400, 0, False)
