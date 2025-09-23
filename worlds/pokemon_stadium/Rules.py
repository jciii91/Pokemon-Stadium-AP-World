from worlds.generic.Rules import set_rule, add_item_rule
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PokemonStadiumWorld

def set_rules(world: "PokemonStadiumWorld"):
    player = world.player
    options = world.options

    # Gym Access
    set_rule(world.multiworld.get_location("Pewter Gym", player), lambda state: state.has("Pewter City Key", player))
    set_rule(world.multiworld.get_location("Cerulean Gym", player), lambda state: state.has("Cerulean City Key", player))
    set_rule(world.multiworld.get_location("Vermillion Gym", player), lambda state: state.has("Vermillion City Key", player))
    set_rule(world.multiworld.get_location("Celadon Gym", player), lambda state: state.has("Celadon City Key", player))
    set_rule(world.multiworld.get_location("Fuchsia Gym", player), lambda state: state.has("Fuchsia City Key", player))
    set_rule(world.multiworld.get_location("Saffron Gym", player), lambda state: state.has("Saffron City Key", player))
    set_rule(world.multiworld.get_location("Cinnabar Gym", player), lambda state: state.has("Cinnabar Island Key", player))
    set_rule(world.multiworld.get_location("Viridian Gym", player), lambda state: state.has("Viridian City Key", player))

    set_rule(world.multiworld.get_location("BROCK", player), lambda state: state.has("Pewter City Key", player))
    set_rule(world.multiworld.get_location("MISTY", player), lambda state: state.has("Cerulean City Key", player))
    set_rule(world.multiworld.get_location("SURGE", player), lambda state: state.has("Vermillion City Key", player))
    set_rule(world.multiworld.get_location("ERIKA", player), lambda state: state.has("Celadon City Key", player))
    set_rule(world.multiworld.get_location("KOGA", player), lambda state: state.has("Fuchsia City Key", player))
    set_rule(world.multiworld.get_location("SABRINA", player), lambda state: state.has("Saffron City Key", player))
    set_rule(world.multiworld.get_location("BLAINE", player), lambda state: state.has("Cinnabar Island Key", player))
    set_rule(world.multiworld.get_location("GIOVANNI", player), lambda state: state.has("Viridian City Key", player))

    # Victory condition rule!
    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
