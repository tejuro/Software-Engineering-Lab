
from hypothesis import given, strategies as st

from house_painting_quote_parser import (
    clean_colour_name,
    room_area,
    total_wall_area
)


# Test 1: Fuzz testing clean_colour_name()
@given(st.text() | st.none())
def test_clean_colour_name_no_crash(s):
    try:
        clean_colour_name(s)
    except Exception as e:
        assert False, f"clean_colour_name crashed with: {e}"


# Test 2: Fuzz testing room_area()
@given(st.text() | st.none())
def test_room_area_no_crash(s):
    try:
        room_area(s)
    except Exception as e:
        assert False, f"room_area crashed with: {e}"


# Test 3: Fuzz testing total_wall_area()
@given(st.text() | st.none())
def test_total_wall_area_no_crash(s):
    try:
        total_wall_area(s)
    except Exception as e:
        assert False, f"total_wall_area crashed with: {e}"
