import imp
from agents import DoubleDQN
from agents import DoubleDuelingDQN
from agents import MCDoubleDuelingDQN
from agents import PPO
from agents import RangeAggression
from agents import RandomStrategy
from agents import SARSA
from actions import vampire_bite
from actions import arrow_shot
from actions import EndTurn
from actions import MoveLeft
from actions import MoveRight
from actions import MoveUp
from actions import MoveDown
from actions import bite, tail_spike
from actions import barbarian_axe_slash, barbarian_axe_slash_reckless
from actions import fire_bolt_cantrip, ray_of_frost_cantrip, chromatic_orb_level_1, magic_missile_level_1, scorching_ray_level_2, aganazzars_scorcher_level_2
from actions import shortsword_slash, handcrossbow_shot
from actions import DoNotMove

from players import dungeon_master
from players import hayden
from utils.dnd_utils import roll_dice


import numpy as np


class Creature:
    """
    Represents a creature
    """
    def __init__(
            self, player, name, hit_points, armor_class, location, strategy,
            speed=30, actions=[], reactions=[], attacks_allowed=1,
            spells_allowed=1, symbol="x", resistance = 0, level_1_spell_slots = 0, level_2_spell_slots = 0):
        self.player = player
        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.armor_class = armor_class
        self.speed = speed
        self.movement_remaining = self.speed
        self.strategy = strategy
        self.actions = [EndTurn()] + actions
        self.reactions = reactions
        self.location = location
        self.attacks_allowed = attacks_allowed
        self.spells_allowed = spells_allowed
        self.attacks_used = 0
        self.spells_used = 0
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.symbol = symbol
        self.action_count = 0
        self.advantage_counter = 0
        self.disadvantage_counter = 0
        self.resistance = resistance
        self.level_1_spell_slots_counter = level_1_spell_slots
        self.level_2_spell_slots_counter = level_2_spell_slots


    def use_action(self, action, **kwargs):
        """
        Uses action
        """
        self.action_count += 1
        combat_handler = kwargs['combat_handler']
        combat_handler.actions_this_round[self] += 1
        return action.use(self, **kwargs)

    def roll_initiative(self):
        """
        Roll initiative
        Todo: Add modifier
        """
        self.action_count = 0
        modifier = 0
        return roll_dice(20) + modifier

    def reset_round_resources(self):
        """
        Resets the following:
            * Movement
            * Number of used attacks
            * Number of used spells
            * Number of used actions
            * Number of used bonus actions
        """

        self.attacks_used = 0
        self.spells_used = 0
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.movement_remaining = self.speed

    def is_alive(self):
        """
        :return:
        """
        if self.hit_points > 0:
            is_alive = True
        else:
            is_alive = False
        return is_alive

    def sample_enemy(self, combat_handler):
        """
        todo: remove self from potential enemies
        :param combat_handler:
        :return:
        """
        creatures = combat_handler.combatants
        creatures = [creature for creature in creatures if creature.name != self.name]
        random_enemy = np.random.choice(creatures)
        return random_enemy
    
    def attack_of_opportunity(self, initial_location, enemy_location):
        x_before = initial_location[0]
        y_before = initial_location[1]
        x_enemy = enemy_location[0]
        y_enemy = enemy_location[1]
        x_after = self.location[0]
        y_after = self.location[1]
        
        withinRangeBefore = ((x_before - x_enemy)**2 + (y_before - y_enemy)**2)**0.5 < 8
        withinRangeAfter = ((x_after - x_enemy)**2 + (y_after - y_enemy)**2)**0.5 < 8
        
        if withinRangeBefore == True and withinRangeAfter == False:
            # print("AOO")
            if self.name == "Strahd":
                self.hit_points -= 3
            else:
                self.hit_points -= 1

    def full_heal(self):
        self.hit_points = self.max_hit_points

    def get_action(self, name):
        """
        :param name:
        :return:
        """
        matching_actions = [action for action in self.actions if action.name == name]
        assert len(matching_actions) == 1, "Exactly 1 action must match the given action name"
        matching_action = matching_actions[0]
        return matching_action

    def initialize(self, combat_handler):
        self.strategy.initialize(creature=self, combat_handler=combat_handler)


# Todo: Move into DB
# vampire = Creature(
#     player=dungeon_master,
#     name="Strahd",
#     hit_points=200,
#     armor_class=17,
#     actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), vampire_bite],
#     location=np.array([5, 5]),
#     symbol="@",
#     strategy=RandomStrategy()
# )

manticore = Creature(
    player=dungeon_master,
    name="Strahd",
    hit_points=80,
    armor_class=14,
    actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), bite, tail_spike],
    level_1_spell_slots = 3,
    location=np.array([5, 5]),
    symbol="@",
    strategy=RandomStrategy()
)

# leotris = Creature(
#     player=hayden,
#     name="Leotris",
#     hit_points=25,
#     armor_class=16,
#     resistance = 0,
#     actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), arrow_shot],
#     location=np.array([5, 10]),
#     symbol="x",
#     strategy=PPO()
# )

barbarian = Creature(
    player=hayden,
    name="Leotris",
    hit_points=32,
    armor_class=14,
    resistance = 1,
    actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), barbarian_axe_slash, barbarian_axe_slash_reckless],
    location=np.array([5, 10]),
    symbol="x",
    strategy=PPO()
)

wizard = Creature(
    player=hayden,
    name="Leotris",
    hit_points=16,
    armor_class=11,
    resistance = 0,
    actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), fire_bolt_cantrip, ray_of_frost_cantrip, chromatic_orb_level_1, magic_missile_level_1, scorching_ray_level_2, aganazzars_scorcher_level_2],
    location=np.array([5, 10]),
    level_1_spell_slots = 3,
    level_2_spell_slots = 1,
    symbol="x",
    strategy=PPO()
)

ranger = Creature(
    player=hayden,
    name="Leotris",
    hit_points=28,
    armor_class=14,
    resistance = 0,
    actions=[MoveLeft(), MoveRight(), MoveUp(), MoveDown(), DoNotMove(), shortsword_slash, handcrossbow_shot],
    location=np.array([5, 10]),
    symbol="x",
    strategy=PPO()
)