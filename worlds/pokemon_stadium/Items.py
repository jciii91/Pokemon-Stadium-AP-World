import logging
import random

from BaseClasses import Item, ItemClassification

from .Types import ItemData, PokemonStadiumItem
from .Locations import get_total_locations
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from . import PokemonStadiumWorld

def create_itempool(world: 'PokemonStadiumWorld') -> List[Item]:
    item_pool: List[Item] = []

    # This is a good place to grab anything you need from options

    for name in pokemon_stadium_items:
        if name != 'Victory' and name not in world.starting_gym_keys:
            item_pool.append(create_item(world, name))

    victory = create_item(world, 'Victory')
    world.multiworld.get_location('Beat Rival', world.player).place_locked_item(victory)

    item_pool += create_junk_items(world, get_total_locations(world) - len(item_pool) - 1)

    return item_pool

def create_item(world: 'PokemonStadiumWorld', name: str) -> Item:
    data = item_table[name]
    return PokemonStadiumItem(name, data.classification, data.ap_code, world.player)

def create_multiple_items(world: "PokemonStadiumWorld", name: str, count: int, item_type: ItemClassification = ItemClassification.progression) -> List[Item]:
    data = item_table[name]
    itemlist: List[Item] = []

    for i in range(count):
        itemlist += [PokemonStadiumItem(name, item_type, data.ap_code, world.player)]

    return itemlist

def create_junk_items(world: 'PokemonStadiumWorld', count: int) -> List[Item]:
    junk_pool: List[Item] = []
    junk_list: Dict[str, int] = {}

    for name in item_table.keys():
        ic = item_table[name].classification
        if ic == ItemClassification.filler:
            junk_list[name] = junk_weights.get(name)

    for _ in range(count):
        junk_pool.append(world.create_item(world.random.choices(list(junk_list.keys()), weights=list(junk_list.values()), k=1)[0]))

    return junk_pool

pokemon_stadium_items = {
    # Progression items
    'Pewter City Key': ItemData(10000001, ItemClassification.progression),
    'Boulder Badge': ItemData(10000002, ItemClassification.progression),
    'Cerulean City Key': ItemData(10000003, ItemClassification.progression),
    'Cascade Badge': ItemData(10000004, ItemClassification.progression),
    'Vermillion City Key': ItemData(10000005, ItemClassification.progression),
    'Thunder Badge': ItemData(10000006, ItemClassification.progression),
    'Celadon City Key': ItemData(10000007, ItemClassification.progression),
    'Rainbow Badge': ItemData(10000008, ItemClassification.progression),
    'Fuchsia City Key': ItemData(10000009, ItemClassification.progression),
    'Soul Badge': ItemData(10000010, ItemClassification.progression),
    'Saffron City Key': ItemData(10000011, ItemClassification.progression),
    'Marsh Badge': ItemData(10000012, ItemClassification.progression),
    'Cinnabar Island Key': ItemData(10000013, ItemClassification.progression),
    'Volcano Badge': ItemData(10000014, ItemClassification.progression),
    'Viridian City Key': ItemData(10000015, ItemClassification.progression),
    'Earth Badge': ItemData(10000016, ItemClassification.progression),

    # Useful items

    # Victory is added here since in this organization it needs to be in the default item pool
    'Victory': ItemData(10000000, ItemClassification.progression)
}

gym_keys = [
    'Pewter City Key',
    'Cerulean City Key',
    'Vermillion City Key',
    'Celadon City Key',
    'Fuchsia City Key',
    'Saffron City Key',
    'Cinnabar Island Key',
    'Viridian City Key',
]

gym_badge_codes = [
    10000002,
    10000004,
    10000006,
    10000008,
    10000010,
    10000012,
    10000014,
    10000016,
]

junk_items = {
    "Pokedoll": ItemData(20050011, ItemClassification.filler, 0),
}

junk_weights = {
    "Pokedoll": 40,
}

item_table = {
    **pokemon_stadium_items,
    **junk_items
}
