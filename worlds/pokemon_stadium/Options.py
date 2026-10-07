from typing import List, Dict, Any
from dataclasses import dataclass
from worlds.AutoWorld import PerGameCommonOptions
from Options import Choice, OptionGroup, Toggle, Range

def create_option_groups() -> List[OptionGroup]:
    option_group_list: List[OptionGroup] = []
    for name, options in pokemon_stadium_option_groups.items():
        option_group_list.append(OptionGroup(name=name, options=options))

    return option_group_list

class VictoryCondition(Choice):
    """
    Choose victory condition. Defeat the Rival at the end of Gym Leader Castle, clear Poké and Prime Master Ball Cups, or both.
    """
    display_name = "Victory Condition"
    option_defeat_rival = 1
    option_clear_master_ball_cups = 2
    option_rival_and_both_cups = 3
    default = 1

class BadgeRequirement(Range):
    """
    Choose how many badges are required to enter the Gym Leader Castle. The default is 8, which is the vanilla requirement.
    """
    display_name = "Badge Requirement"
    range_start = 0
    range_end = 8
    default = 8

class StartingKeyCount(Range):
    """
    Choose how many Gym Keys you start with. The default is 3.
    """
    display_name = "Starting Key Count"
    range_start = 0
    range_end = 8
    default = 3

class ProgressiveGLC(Toggle):
    """
    Toggle on to unlock gyms progressively instead of randomly.
    The gym keys will be replaced with Progressive Gym Keys. Each key received unlocks the next gym.
    This option is off by default.
    """
    display_name = 'Progressive Gym Leader Castle'
    option_off = 0
    option_on = 1
    default = 0

class Trainersanity(Toggle):
    """
    Toggle on to make all Trainers into checks. This option is off by default.
    """
    display_name = 'Trainersanity'
    option_off = 0
    option_on = 1
    default = 0

class BaseStatTotalRandomness(Choice):
    """
    Controls the level of randomness for Pokemon BST. Stat distribution per Pokemon will follow a randomly selected distribution curve.
    The higher the selection, the more extreme a curve you may see used. 
    Stat changes are universal. Rental Pokemon and enemy trainer team Pokemon use the same BSTs.
    Vanilla - No change
    Low - 3 distribution types
    Medium - 4 distribution types
    High - 5 distribution types
    """
    display_name = "BST Randomness"
    option_vanilla = 1
    option_low = 2
    option_medium = 3
    option_high = 4
    default = 1

class RentalRandomness(Toggle):
    """
    Toggle on to randomize rental Pokemon. This option is off by default.
    """
    display_name = 'Rental Randomness'
    option_off = 0
    option_on = 1
    default = 0

class RentalListShuffle(Choice):
    """
    Controls whether the rental pokemon list is randomized or not.
    Instead of going in dex order, the rental tables will be shuffled.

    Vanilla - No change
    Sorted - Sorted by adjusted BST, which is calculated using the base BST and a Pokemon's moveset
    Random - Fully randomized, with no regard to BST or moveset
    """
    display_name = "Rental List Shuffle"
    option_vanilla = 0
    option_sorted = 1
    option_randomized = 2
    default = 0

class TrainerRandomness(Toggle):
    """
    Toggle on to randomize enemy trainer teams. This option is off by default.
    """
    display_name = 'Trainer Randomness'
    option_off = 0
    option_on = 1
    default = 0

@dataclass
class PokemonStadiumOptions(PerGameCommonOptions):
    VictoryCondition:           VictoryCondition
    BadgeRequirement:           BadgeRequirement
    StartingKeyCount:           StartingKeyCount
    ProgressiveGLC:             ProgressiveGLC
    BaseStatTotalRandomness:    BaseStatTotalRandomness
    RentalRandomness:           RentalRandomness
    RentalListShuffle:          RentalListShuffle
    TrainerRandomness:          TrainerRandomness
    Trainersanity:              Trainersanity

pokemon_stadium_option_groups: Dict[str, List[Any]] = {
    "General Options": [
        VictoryCondition,
        BadgeRequirement,
        StartingKeyCount,
        ProgressiveGLC,
        Trainersanity,
    ],
    "Randomizer Options": [
        BaseStatTotalRandomness,
        RentalRandomness,
        RentalListShuffle,
        TrainerRandomness,
    ],
}
