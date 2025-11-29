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
    Choose victory condition
    """
    display_name = "Victory Condition"
    option_defeat_rival = 1
    option_clear_master_ball_cup = 2
    default = 1

class GymCastleTrainerRandomness(Choice):
    """
    Controls the level of randomness for the enemy team moves in Gym Leader Castle.
    Vanilla - No change
    Low - Movesets have a status, STAB, and higher attack stat aligned move. (4th move is fully random)
    Medium - Movesets have a STAB, and higher attack stat aligned move. (3rd and 4th moves are fully random)
    High - Movesets have a higher attack stat aligned move. (all other moves are fully random)
    """
    display_name = "Gym Castle Trainer Randomness"
    option_vanilla = 1
    option_low = 2
    option_medium = 3
    option_high = 4
    default = 1

class GymCastleRentalRandomness(Choice):
    """
    Controls the level of randomness for the rental Pokemon moves in Gym Leader Castle.
    Vanilla - No change
    Low - Movesets have a status, STAB, and higher attack stat aligned move. (4th move is fully random)
    Medium - Movesets have a STAB, and higher attack stat aligned move. (3rd and 4th moves are fully random)
    High - Movesets have a higher attack stat aligned move. (all other moves are fully random)
    """
    display_name = "Gym Castle Rental Randomness"
    option_vanilla = 1
    option_low = 2
    option_medium = 3
    option_high = 4
    default = 1

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

@dataclass
class PokemonStadiumOptions(PerGameCommonOptions):
    VictoryCondition:           VictoryCondition
    GymCastleTrainerRandomness: GymCastleTrainerRandomness
    GymCastleRentalRandomness:  GymCastleRentalRandomness
    BaseStatTotalRandomness:    BaseStatTotalRandomness

# This is where you organize your options
# Its entirely up to you how you want to organize it
pokemon_stadium_option_groups: Dict[str, List[Any]] = {
    "General Options": [
        VictoryCondition,
        BaseStatTotalRandomness,
        GymCastleRentalRandomness,
        GymCastleTrainerRandomness,
    ],
}
