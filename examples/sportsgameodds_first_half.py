"""Utility helpers for retrieving first-half goal odds from SportsGameOdds.

The script mirrors the manual steps described in the SportsGameOdds docs:

1. Fetch the soccer sport configuration (``/sports``).
2. Identify the first-half period identifier from ``basePeriods``/``extraPeriods``.
3. Fetch the goals/stat identifier from ``/stats``.
4. Select a league and event for a target date.
5. Query ``/odds`` with the collected identifiers.

The functions are intentionally composable so they can be copied into a
Streamlit app or other service that needs to power a first-half goal betting
experience.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from typing import Dict, Iterable, List, Optional

import requests

BASE_URL = "https://api.sportsgameodds.com/v1"
DEFAULT_TIMEOUT = 10


@dataclass
class SportConfig:
    """Minimal information needed from the ``/sports`` endpoint."""

    sport_id: str
    name: str
    first_half_period_id: str


@dataclass
class League:
    league_id: str
    name: str


@dataclass
class Event:
    event_id: str
    name: str


def _get_json(path: str, api_key: str, params: Optional[Dict[str, str]] = None) -> Dict:
    """Perform a GET request and return the JSON payload."""

    headers = {"x-api-key": api_key}
    response = requests.get(
        f"{BASE_URL}{path}", headers=headers, params=params or {}, timeout=DEFAULT_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def _find_first_half_period(periods: Iterable[Dict[str, str]]) -> str:
    """Locate the periodID that represents the first half."""

    for period in periods:
        name = period.get("name", "").lower()
        if "1st half" in name or "first half" in name:
            return period["periodID"]
    raise ValueError("Could not find a first-half period in the provided data")


def get_soccer_config(api_key: str, sport_keyword: str = "soccer") -> SportConfig:
    """Retrieve the soccer sport configuration, including the first-half period."""

    sports: List[Dict[str, str]] = _get_json("/sports", api_key)
    for sport in sports:
        if sport_keyword.lower() in sport["name"].lower():
            period_id = _find_first_half_period(
                sport.get("basePeriods", []) + sport.get("extraPeriods", [])
            )
            return SportConfig(
                sport_id=sport["sportID"],
                name=sport["name"],
                first_half_period_id=period_id,
            )
    raise ValueError(f"Sport containing keyword '{sport_keyword}' was not found")


def get_goals_stat_id(api_key: str, sport_id: str) -> str:
    """Return the statID corresponding to goals/points for the sport."""

    stats: List[Dict[str, str]] = _get_json("/stats", api_key, params={"sportID": sport_id})
    for stat in stats:
        if stat["statID"].lower() == "points":
            return stat["statID"]
    raise ValueError("No 'points' statID was found for the requested sport")


def get_league(api_key: str, sport_id: str, league_keyword: Optional[str] = None) -> League:
    """Select a league, optionally filtering by a keyword in the name."""

    leagues: List[Dict[str, str]] = _get_json("/leagues", api_key, params={"sportID": sport_id})
    if league_keyword:
        for league in leagues:
            if league_keyword.lower() in league["name"].lower():
                return League(league_id=league["leagueID"], name=league["name"])
        raise ValueError(f"No league matched keyword '{league_keyword}'")
    if not leagues:
        raise ValueError("No leagues returned for the selected sport")
    top_league = leagues[0]
    return League(league_id=top_league["leagueID"], name=top_league["name"])


def get_event(
    api_key: str,
    sport_id: str,
    league_id: str,
    target_date: date,
) -> Event:
    """Fetch the first event for the league/date combination."""

    params = {
        "sportID": sport_id,
        "leagueID": league_id,
        "date": target_date.isoformat(),
    }
    events: List[Dict[str, str]] = _get_json("/events", api_key, params=params)
    if not events:
        raise ValueError(
            f"No events returned for league '{league_id}' on {target_date.isoformat()}"
        )
    event = events[0]
    return Event(event_id=event["eventID"], name=event["name"])


def get_first_half_goal_odds(
    api_key: str,
    sport_id: str,
    league_id: str,
    event_id: str,
    stat_id: str,
    period_id: str,
    bet_type_id: Optional[str] = None,
) -> Dict:
    """Retrieve first-half odds for goals/points via the ``/odds`` endpoint."""

    params = {
        "sportID": sport_id,
        "leagueID": league_id,
        "eventID": event_id,
        "statID": stat_id,
        "periodID": period_id,
    }
    if bet_type_id:
        params["betTypeID"] = bet_type_id
    return _get_json("/odds", api_key, params=params)


def demo() -> None:
    """Demonstrate fetching first-half goal odds for today's first soccer match."""

    api_key = os.environ.get("SPORTSGAMEODDS_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Please set the SPORTSGAMEODDS_API_KEY environment variable before running the demo."
        )

    soccer = get_soccer_config(api_key)
    stat_id = get_goals_stat_id(api_key, soccer.sport_id)
    league = get_league(api_key, soccer.sport_id)
    event = get_event(api_key, soccer.sport_id, league.league_id, date.today())
    odds = get_first_half_goal_odds(
        api_key,
        soccer.sport_id,
        league.league_id,
        event.event_id,
        stat_id,
        soccer.first_half_period_id,
    )

    print("Sport:", soccer)
    print("League:", league)
    print("Event:", event)
    print("Odds response:")
    print(odds)


if __name__ == "__main__":
    demo()
