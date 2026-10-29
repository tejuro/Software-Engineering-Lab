
import pytest

from house_painting_quote import painting_quote, paint_litres, crew_days


# painting_quote: valid and invalid paths

def test_painting_quote_invalid_paint():
    with pytest.raises(ValueError, match="unknown paint"):
        painting_quote("unknown", 100, 1, False)


def test_painting_quote_invalid_area():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 0, 1, False)


def test_painting_quote_invalid_coats():
    with pytest.raises(ValueError, match="invalid job"):
        painting_quote("emulsion", 100, 0, False)


def test_distemper_exterior():
    with pytest.raises(ValueError, match="distemper is for interiors only"):
        painting_quote("distemper", 100, 1, True)


def test_interior_minimum_cost():
    assert painting_quote("distemper", 100, 1, False) == 5000


def test_exterior_cost():
    assert painting_quote("enamel", 500, 2, True) == 32500


def test_large_area_discount():
    assert painting_quote("emulsion", 2001, 1, False) == 36018


# paint_litres: both surface branches and rounding

def test_smooth_surface():
    assert paint_litres(200, 1, "smooth") == 2


def test_rough_surface():
    assert paint_litres(120, 1, "rough") == 2


def test_unknown_surface():
    with pytest.raises(ValueError, match="unknown surface"):
        paint_litres(100, 1, "unknown")


def test_exact_litre_calculation():
    assert paint_litres(200, 1, "smooth") == 2


def test_litre_rounding_up():
    assert paint_litres(201, 1, "smooth") == 3


# crew_days: valid, invalid, rounding and wallpaper branches

def test_invalid_painters():
    with pytest.raises(ValueError, match="need at least one painter"):
        crew_days(400, 0, False)


def test_exact_crew_days():
    assert crew_days(800, 2, False) == 1


def test_crew_days_rounding_up():
    assert crew_days(801, 2, False) == 2


def test_wallpaper_removal():
    assert crew_days(400, 1, True) == 3


def test_no_wallpaper_removal():
    assert crew_days(400, 1, False) == 1
