"""
Given two teams, simulate a match and produce
commentary events.
"""

import random

from domain.models.models import MatchEvent, Match, Team


class MatchEngine:
    """Simulates a fictional soccer match between two teams.

    Commentary is driven by player names and positions so every match
    feels unique. The stronger team (by total_soccer_power) wins more
    often but upsets are possible.
    """

    _GOAL_TEMPLATES = [
        "{scorer} fires a stunning shot past {goalie}!",
        "{scorer} breaks through the defence and scores!",
        "{scorer} with a perfectly placed header — goal!",
        "{scorer} latches onto a loose ball and slots it home!",
        "{scorer} beats {goalie} with a powerful strike from distance!",
        "What a run from {scorer}! {goalie} had no chance!",
        "{scorer} taps in from close range — too easy!",
        "{scorer} curls it beautifully into the top corner!",
    ]

    _MISS_TEMPLATES = [
        "{player} blazes it over the bar!",
        "{player} drags it wide — so close!",
        "{player} hits the post — unlucky!",
        "{goalie} pulls off a magnificent save to deny {player}!",
        "{player}'s shot is blocked by the defender!",
    ]

    _CARD_TEMPLATES = [
        "{player} receives a yellow card for a late tackle.",
        "Referee books {player} for simulation — harsh decision!",
    ]

    def simulate(self, home: Team, away: Team) -> Match:
        random.seed()
        events: list[MatchEvent] = []
        home_score = 0
        away_score = 0

        home_power = home.total_soccer_power
        away_power = away.total_soccer_power
        total_power = home_power + away_power

        home_goal_prob = home_power / total_power
        num_events = random.randint(18, 28)
        minutes = sorted(random.sample(range(1, 91), num_events))

        for minute in minutes:
            event_roll = random.random()

            if event_roll < 0.35:
                if random.random() < home_goal_prob:
                    scorer = random.choice(home.attackers + home.defenders)
                    goalie = away.goalie
                    home_score += 1
                    text = random.choice(self._GOAL_TEMPLATES).format(
                        scorer=scorer.name, goalie=goalie.name
                    )
                else:
                    scorer = random.choice(away.attackers + away.defenders)
                    goalie = home.goalie
                    away_score += 1
                    text = random.choice(self._GOAL_TEMPLATES).format(
                        scorer=scorer.name, goalie=goalie.name
                    )
            elif event_roll < 0.70:
                all_players = list(home.players) + list(away.players)
                player = random.choice(all_players)
                if player.universe == home.universe:
                    goalie = away.goalie
                else:
                    goalie = home.goalie
                text = random.choice(self._MISS_TEMPLATES).format(
                    player=player.name, goalie=goalie.name
                )
            else:
                all_players = list(home.players) + list(away.players)
                player = random.choice(all_players)
                text = random.choice(self._CARD_TEMPLATES).format(player=player.name)

            events.append(MatchEvent(minute=minute, text=text))

        events.append(MatchEvent(
            minute=90,
            text=f"Full time! {home.universe.value.replace('_', ' ').title()} {home_score} - "
                 f"{away_score} {away.universe.value.replace('_', ' ').title()}",
        ))

        return Match(
            home_team=home,
            away_team=away,
            home_score=home_score,
            away_score=away_score,
            events=tuple(events),
        )
