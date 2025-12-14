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
    'Pewter Gym':           LocData(20000010, 'Gym Leader Castle'),
    'BROCK':                LocData(20000011, 'Gym Leader Castle'),
    'Cerulean Gym':         LocData(20000020, 'Gym Leader Castle'),
    'MISTY':                LocData(20000021, 'Gym Leader Castle'),
    'Vermillion Gym':       LocData(20000030, 'Gym Leader Castle'),
    'SURGE':                LocData(20000031, 'Gym Leader Castle'),
    'Celadon Gym':          LocData(20000040, 'Gym Leader Castle'),
    'ERIKA':                LocData(20000041, 'Gym Leader Castle'),
    'Fuchsia Gym':          LocData(20000050, 'Gym Leader Castle'),
    'KOGA':                 LocData(20000051, 'Gym Leader Castle'),
    'Saffron Gym':          LocData(20000060, 'Gym Leader Castle'),
    'SABRINA':              LocData(20000061, 'Gym Leader Castle'),
    'Cinnabar Gym':         LocData(20000070, 'Gym Leader Castle'),
    'BLAINE':               LocData(20000071, 'Gym Leader Castle'),
    'Viridian Gym':         LocData(20000080, 'Gym Leader Castle'),
    'GIOVANNI':             LocData(20000081, 'Gym Leader Castle'),
    'Magikarp\'s Splash':   LocData(20000100, 'Kids Club'),
    'Clefairy Says':        LocData(20000101, 'Kids Club'),
    'Run, Rattata, Run':    LocData(20000102, 'Kids Club'),
    'Snore War':            LocData(20000103, 'Kids Club'),
    'Thundering Dynamo':    LocData(20000104, 'Kids Club'),
    'Sushi-Go-Round':       LocData(20000105, 'Kids Club'),
    'Ekans\'s Hoop Hurl':   LocData(20000106, 'Kids Club'),
    'Rock Harden':          LocData(20000107, 'Kids Club'),
    'Dig! Dig! Dig!':       LocData(20000108, 'Kids Club'),
}

event_locations = {
    'Beat Rival': LocData(20000000, 'Hall of Fame')
}

location_table = {
    **pokemon_stadium_locations,
    **event_locations
}
