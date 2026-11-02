from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_SPLIT_RE = re.compile(r"[,;|•·/–—]| - ")
_PAREN_RE = re.compile(r"\([^)]*\)")


@dataclass(slots=True)
class LocationResult:
    city: str | None = None
    province: str | None = None
    is_in_java: int | None = None
    is_indonesia: int | None = None
    verified: bool = False


def _norm(text: str) -> str:
    out = text.lower().strip()
    out = re.sub(r"\b(kota|kabupaten|kab\.?|provinsi|prov\.?|daerah khusus ibukota)\b", " ", out)
    out = re.sub(r"[^\w\s]", " ", out)
    return re.sub(r"\s+", " ", out).strip()


class LocationNormalizer:
    def __init__(self, config_path: str | Path) -> None:
        with Path(config_path).open(encoding="utf-8") as fh:
            data: dict[str, Any] = yaml.safe_load(fh) or {}
        self.aliases: dict[str, tuple[str | None, str | None, int | None]] = {}
        self.foreign: set[str] = set()
        self.indonesia: set[str] = set()
        self.remote_words: set[str] = set()

        for prov in data.get("provinces", []):
            jv = int(prov.get("is_java", 1))
            for name in [prov["name"], *prov.get("aliases", [])]:
                self.aliases[_norm(name)] = (None, prov["name"], jv)
            for region in prov.get("regions", []):
                self.aliases[_norm(region)] = (None, prov["name"], jv)
            for city in prov.get("cities", []):
                for name in [city["name"], *city.get("aliases", [])]:
                    self.aliases[_norm(name)] = (city["name"], prov["name"], jv)
        for prov in data.get("outside_java_provinces", []):
            self.aliases[_norm(prov)] = (None, prov, 0)
        for city in data.get("outside_java_cities", []):
            self.aliases[_norm(city["name"])] = (city["name"], city["province"], 0)
        self.indonesia = {_norm(x) for x in data.get("country_id", [])}
        self.foreign = {_norm(x) for x in data.get("country_foreign", [])}
        self.remote_words = {_norm(x) for x in data.get("remote_words", [])}
        self._keys_by_len = sorted(self.aliases, key=len, reverse=True)

    def _lookup(self, segment: str) -> tuple[str | None, str | None, int | None] | None:
        seg = _norm(segment)
        if not seg:
            return None
        if seg in self.aliases:
            return self.aliases[seg]
        padded = f" {seg} "
        for alias in self._keys_by_len:
            if f" {alias} " in padded:
                return self.aliases[alias]
        return None

    def normalize(self, raw: str | None) -> LocationResult:
        if not raw:
            return LocationResult()
        text = _PAREN_RE.sub(" ", raw)
        segments = [s for s in _SPLIT_RE.split(text) if s and s.strip()]

        city = province = None
        is_java: int | None = None
        verified = False
        foreign_hit = False
        indonesia_hit = False

        for segment in segments:
            lowered = _norm(segment)
            if lowered in self.remote_words:
                continue
            if lowered in self.indonesia:
                indonesia_hit = True
                continue
            if lowered in self.foreign:
                foreign_hit = True
                continue
            hit = self._lookup(segment)
            if hit:
                c, p, jv = hit
                verified = True
                indonesia_hit = True
                if city is None and c:
                    city = c
                if province is None and p:
                    province = p
                if jv == 1:
                    is_java = 1
                elif is_java is None:
                    is_java = jv

        if not indonesia_hit and foreign_hit:
            is_indonesia = 0
        elif indonesia_hit:
            is_indonesia = 1
        else:
            is_indonesia = None

        return LocationResult(
            city=city,
            province=province,
            is_in_java=is_java,
            is_indonesia=is_indonesia,
            verified=verified,
        )


def accept_location(work_mode: str, loc: LocationResult, keep_unverified: bool) -> bool:
    if loc.is_indonesia == 0:
        return False
    if work_mode == "remote":
        return True
    if loc.is_in_java == 1:
        return True
    if loc.is_in_java == 0:
        return False
    return keep_unverified
