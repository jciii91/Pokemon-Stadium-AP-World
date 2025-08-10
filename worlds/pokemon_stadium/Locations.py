from typing import Dict, TYPE_CHECKING
import logging

from .Types import LocData

if TYPE_CHECKING:
    from . import PokemonStadiumWorld

def get_total_locations(world: 'PokemonStadiumWorld') -> int:
    return len(location_table)

def get_location_names() -> Dict[str, int]:
    names = {name: data.ap_code for name, data in location_table.items()}

    return names

def is_valid_location(world: 'PokemonStadiumWorld', name) -> bool:
    return True

pokemon_stadium_locations = {
    'Pewter Gym':       LocData(20000010, 'Gym Leader Castle'),
    'Brock':            LocData(20000011, 'Pewter Gym'),
    'Cerulean Gym':     LocData(20000020, 'Gym Leader Castle'),
    'Misty':            LocData(20000021, 'Cerulean Gym'),
    'Vermillion Gym':   LocData(20000030, 'Gym Leader Castle'),
    'Surge':            LocData(20000031, 'Vermillion Gym'),
    'Celadon Gym':      LocData(20000040, 'Gym Leader Castle'),
    'Erika':            LocData(20000041, 'Celadon Gym'),
    'Fuchsia Gym':      LocData(20000050, 'Gym Leader Castle'),
    'Koga':             LocData(20000051, 'Fuchsia Gym'),
    'Saffron Gym':      LocData(20000060, 'Gym Leader Castle'),
    'Sabrina':          LocData(20000061, 'Saffron Gym'),
    'Cinnabar Gym':     LocData(20000070, 'Gym Leader Castle'),
    'Blaine':           LocData(20000071, 'Cinnabar Gym'),
    'Viridian Gym':     LocData(20000080, 'Gym Leader Castle'),
    'Giovanni':         LocData(20000081, 'Viridian Gym'),
}

event_locations = {
    'Beat Rival': LocData(20000000, 'Hall of Fame')
}

location_table = {
    **pokemon_stadium_locations,
    **event_locations
}
