import pytest

from domain.models.models import Lineup, Player, Position, Universe
from domain.team_assembler import TeamAssembler


def make_player(name: str, height_cm: float, weight_kg: float) -> Player:
    return Player(name=name, height_cm=height_cm, weight_kg=weight_kg, universe=Universe.STAR_WARS)


FIVE_PLAYERS = [
    make_player("Tall Terry", 200, 80),
    make_player("Heavy Harry", 170, 120),
    make_player("Beefy Bob", 175, 110),
    make_player("Short Sam", 150, 60),
    make_player("Petite Pat", 155, 65),
]


class TestLineup:
    def test_valid_default(self):
        lineup = Lineup()
        assert lineup.defenders == 2 and lineup.attackers == 2

    def test_valid_asymmetric(self):
        assert Lineup(defenders=1, attackers=3).defenders == 1

    def test_invalid_sum_raises(self):
        with pytest.raises(ValueError, match="must equal 4"):
            Lineup(defenders=3, attackers=3)

    def test_zero_defenders_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            Lineup(defenders=0, attackers=4)


class TestPlayerSoccerPower:
    def test_formula(self):
        # 100*0.4 + 100*0.6 = 100
        assert make_player("P", 100, 100).soccer_power == 100.0

    def test_with_position_preserves_stats(self):
        p = make_player("P", 180, 75)
        pos = p.with_position(Position.GOALIE)
        assert pos.position == Position.GOALIE
        assert p.position is None  # original unchanged


class TestTeamAssembler:
    def setup_method(self):
        self.assembler = TeamAssembler()
        self.lineup = Lineup(defenders=2, attackers=2)

    def test_goalie_is_tallest(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        assert team.goalie.name == "Tall Terry"

    def test_defenders_are_heaviest(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        assert {p.name for p in team.defenders} == {"Heavy Harry", "Beefy Bob"}

    def test_attackers_are_shortest(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        assert {p.name for p in team.attackers} == {"Short Sam", "Petite Pat"}

    def test_all_players_have_positions(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        assert all(p.position is not None for p in team.players)

    def test_exactly_five_players(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        assert len(team.players) == 5

    def test_asymmetric_1_3(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, Lineup(defenders=1, attackers=3))
        assert len(team.defenders) == 1 and len(team.attackers) == 3

    def test_asymmetric_3_1(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, Lineup(defenders=3, attackers=1))
        assert len(team.defenders) == 3 and len(team.attackers) == 1

    def test_too_few_players_raises(self):
        with pytest.raises(ValueError, match="at least 5"):
            self.assembler.assemble(FIVE_PLAYERS[:3], Universe.STAR_WARS, self.lineup)

    def test_no_player_duplicated(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        names = [p.name for p in team.players]
        assert len(names) == len(set(names))

    def test_total_soccer_power(self):
        team = self.assembler.assemble(FIVE_PLAYERS, Universe.STAR_WARS, self.lineup)
        expected = round(sum(p.soccer_power for p in team.players), 2)
        assert team.total_soccer_power == expected
