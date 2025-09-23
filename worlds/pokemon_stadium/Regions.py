from BaseClasses import Region
from .Types import PokemonStadiumLocation
from .Locations import location_table, is_valid_location
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PokemonStadiumWorld

def create_regions(world: "PokemonStadiumWorld"):
    menu = create_region(world, "Menu")

    # ---------------------------------- Gym Leader Castle ----------------------------------    
    gym_leader_castle = create_region_and_connect(world, "Gym Leader Castle", "Menu -> Gym Leader Castle", menu)

    create_region_and_connect(world, "Elite Four", "Gym Leader Castle -> Elite Four", gym_leader_castle)
    create_region_and_connect(world, "Rival", "Elite Four -> Rival", gym_leader_castle)
    create_region_and_connect(world, "Hall of Fame", "Rival -> Hall of Fame", gym_leader_castle)
    create_region_and_connect(world, "Beat Rival", "Hall of Fame -> Beat Rival", gym_leader_castle)

def create_region(world: "PokemonStadiumWorld", name: str) -> Region:
    reg = Region(name, world.player, world.multiworld)

    for (key, data) in location_table.items():
        if data.region == name:
            if not is_valid_location(world, key):
                continue
            location = PokemonStadiumLocation(world.player, key, data.ap_code, reg)
            reg.locations.append(location)
    
    world.multiworld.regions.append(reg)
    return reg

def create_region_and_connect(world: "PokemonStadiumWorld", name: str, entrancename: str, connected_region: Region) -> Region:
    reg: Region = create_region(world, name)
    connected_region.connect(reg, entrancename)
    return reg
