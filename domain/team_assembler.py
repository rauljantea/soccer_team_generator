"""Domain service — TeamAssembler.

Rules:
  - Goalie:  the tallest player
  - Defence: the heaviest remaining players (n = lineup.defenders)
  - Offence: the shortest remaining players  (n = lineup.attackers)
"""

from domain.models.models import Lineup, Player, Position, Team, Universe


class TeamAssembler:
    """Assembles a Team from a pool of Player objects.

    This is a domain service: it knows the business rules but has no I/O.
    """

    def assemble(
        self,
        players: list[Player],
        universe: Universe,
        lineup: Lineup,
    ) -> Team:
        if len(players) < lineup.TOTAL_PLAYERS:
            raise ValueError(
                f"Need at least {lineup.TOTAL_PLAYERS} players, "
                f"got {len(players)}"
            )

        pool = players[: lineup.TOTAL_PLAYERS]

        # 1. Goalie — tallest
        tallest = max(pool, key=lambda p: p.height_cm)
        assigned: dict[str, Player] = {tallest.name: tallest.with_position(Position.GOALIE)}
        remaining = [p for p in pool if p.name not in assigned]

        # 2. Defence — heaviest
        by_weight_desc = sorted(remaining, key=lambda p: p.weight_kg, reverse=True)
        for player in by_weight_desc[: lineup.defenders]:
            assigned[player.name] = player.with_position(Position.DEFENCE)
        remaining = [p for p in pool if p.name not in assigned]

        # 3. Offence — shortest
        by_height_asc = sorted(remaining, key=lambda p: p.height_cm)
        for player in by_height_asc[: lineup.attackers]:
            assigned[player.name] = player.with_position(Position.OFFENCE)

        return Team(
            universe=universe,
            players=tuple(assigned.values()),
            lineup=lineup,
        )
