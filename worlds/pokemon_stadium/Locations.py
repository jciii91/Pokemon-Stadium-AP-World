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
    'Pewter Gym - Bug Boy':     LocData(20000011, 'Gym Leader Castle'),
    'Pewter Gym - Lad':         LocData(20000012, 'Gym Leader Castle'),
    'Pewter Gym - Jr♂':         LocData(20000013, 'Gym Leader Castle'),
    'BROCK':                    LocData(20000014, 'Gym Leader Castle'),
    'Pewter Gym':               LocData(20000015, 'Gym Leader Castle'),
    'Cerulean Gym - Fisher':    LocData(20000021, 'Gym Leader Castle'),
    'Cerulean Gym - Jr♀':       LocData(20000022, 'Gym Leader Castle'),
    'Cerulean Gym - Swimmer':   LocData(20000023, 'Gym Leader Castle'),
    'MISTY':                    LocData(20000024, 'Gym Leader Castle'),
    'Cerulean Gym':             LocData(20000025, 'Gym Leader Castle'),
    'Vermillion Gym - Sailor':  LocData(20000031, 'Gym Leader Castle'),
    'Vermillion Gym - Rocker':  LocData(20000032, 'Gym Leader Castle'),
    'Vermillion Gym - Old Man': LocData(20000033, 'Gym Leader Castle'),
    'SURGE':                    LocData(20000034, 'Gym Leader Castle'),
    'Vermillion Gym':           LocData(20000035, 'Gym Leader Castle'),
    'Celadon Gym - Lass':       LocData(20000041, 'Gym Leader Castle'),
    'Celadon Gym - Beauty':     LocData(20000042, 'Gym Leader Castle'),
    'Celadon Gym - Cool♀':      LocData(20000043, 'Gym Leader Castle'),
    'ERIKA':                    LocData(20000044, 'Gym Leader Castle'),
    'Celadon Gym':              LocData(20000045, 'Gym Leader Castle'),
    'Fuchsia Gym - Biker':      LocData(20000051, 'Gym Leader Castle'),
    'Fuchsia Gym - Tamer':      LocData(20000052, 'Gym Leader Castle'),
    'Fuchsia Gym - Juggler':    LocData(20000053, 'Gym Leader Castle'),
    'KOGA':                     LocData(20000054, 'Gym Leader Castle'),
    'Fuchsia Gym':              LocData(20000055, 'Gym Leader Castle'),
    'Saffron Gym - Cue Ball':   LocData(20000061, 'Gym Leader Castle'),
    'Saffron Gym - Burglar':    LocData(20000062, 'Gym Leader Castle'),
    'Saffron Gym - Medium':     LocData(20000063, 'Gym Leader Castle'),
    'SABRINA':                  LocData(20000064, 'Gym Leader Castle'),
    'Saffron Gym':              LocData(20000065, 'Gym Leader Castle'),
    'Cinnabar Gym - Judoboy':   LocData(20000071, 'Gym Leader Castle'),
    'Cinnabar Gym - Psychic':   LocData(20000072, 'Gym Leader Castle'),
    'Cinnabar Gym - Nerd':      LocData(20000073, 'Gym Leader Castle'),
    'BLAINE':                   LocData(20000074, 'Gym Leader Castle'),
    'Cinnabar Gym':             LocData(20000075, 'Gym Leader Castle'),
    'Viridian Gym - Rocket':    LocData(20000081, 'Gym Leader Castle'),
    'Viridian Gym - Lab Man':   LocData(20000082, 'Gym Leader Castle'),
    'Viridian Gym - Cool♂':     LocData(20000083, 'Gym Leader Castle'),
    'GIOVANNI':                 LocData(20000084, 'Gym Leader Castle'),
    'Viridian Gym':             LocData(20000085, 'Gym Leader Castle'),
    'Magikarp\'s Splash':       LocData(20000100, 'Kids Club'),
    'Clefairy Says':            LocData(20000101, 'Kids Club'),
    'Run, Rattata, Run':        LocData(20000102, 'Kids Club'),
    'Snore War':                LocData(20000103, 'Kids Club'),
    'Thundering Dynamo':        LocData(20000104, 'Kids Club'),
    'Sushi-Go-Round':           LocData(20000105, 'Kids Club'),
    'Ekans\'s Hoop Hurl':       LocData(20000106, 'Kids Club'),
    'Rock Harden':              LocData(20000107, 'Kids Club'),
    'Dig! Dig! Dig!':           LocData(20000108, 'Kids Club'),
}

event_locations = {
    'Beat Rival': LocData(20000000, 'Hall of Fame')
}

location_table = {
    **pokemon_stadium_locations,
    **event_locations
}
