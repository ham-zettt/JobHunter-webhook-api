from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import get_settings
from app.pipeline.location import LocationNormalizer, accept_location


@pytest.fixture(scope="module")
def loc() -> LocationNormalizer:
    return LocationNormalizer(Path(get_settings().config_dir) / "locations_java.yaml")


def test_city_and_province(loc):
    res = loc.normalize("Jakarta Selatan, DKI Jakarta")
    assert (res.city, res.province, res.is_in_java, res.is_indonesia, res.verified) == (
        "Jakarta Selatan",
        "DKI Jakarta",
        1,
        1,
        True,
    )


def test_city_alias(loc):
    res = loc.normalize("BSD, Tangerang")
    assert res.city == "Tangerang" and res.province == "Banten" and res.is_in_java == 1


def test_tangsel_alias(loc):
    res = loc.normalize("Tangsel")
    assert res.city == "Tangerang Selatan" and res.province == "Banten"


def test_city_inherits_province(loc):
    res = loc.normalize("Bandung")
    assert res.city == "Bandung" and res.province == "Jawa Barat" and res.is_in_java == 1


def test_outside_java(loc):
    res = loc.normalize("Medan, Sumatera Utara")
    assert res.is_in_java == 0 and res.is_indonesia == 1


def test_foreign_country(loc):
    res = loc.normalize("Singapore")
    assert res.is_in_java is None and res.is_indonesia == 0


def test_unknown_location(loc):
    res = loc.normalize("Lokasi rahasia")
    assert res.verified is False and res.is_indonesia is None


def test_accept_location_rules(loc):
    jakarta = loc.normalize("Jakarta")
    singapore = loc.normalize("Singapore")
    unknown = loc.normalize("Tidak diketahui")

    assert accept_location("onsite", jakarta, keep_unverified=True) is True
    assert accept_location("hybrid", singapore, keep_unverified=True) is False
    assert accept_location("remote", singapore, keep_unverified=True) is False
    assert accept_location("remote", jakarta, keep_unverified=True) is True
    assert accept_location("remote", unknown, keep_unverified=True) is True
    assert accept_location("onsite", unknown, keep_unverified=True) is True
    assert accept_location("onsite", unknown, keep_unverified=False) is False
