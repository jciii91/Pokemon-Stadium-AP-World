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

    # Place items dependent on options
    victory_condition = world.options.VictoryCondition.value
    victory = create_item(world, 'Victory')

    if victory_condition == 1:
        world.multiworld.get_location('Beat Rival', world.player).place_locked_item(victory)
    elif victory_condition == 2:
        world.multiworld.get_location('Master Ball Cups Cleared', world.player).place_locked_item(victory)
    elif victory_condition == 3:
        world.multiworld.get_location('Beat Rival and Clear Both Master Ball Cups', world.player).place_locked_item(victory)

    # Place progression items
    for name in pokemon_stadium_items:
        if name != 'Victory' and name not in world.starting_gym_keys:
            item_pool.append(create_item(world, name))

    item_pool += create_multiple_items(world, 'Poké Cup - Tier Upgrade', 3, ItemClassification.progression)
    item_pool += create_multiple_items(world, 'Prime Cup - Tier Upgrade', 3, ItemClassification.progression)

    # Place useful items
    upgrade_count = 30 if world.options.Trainersanity.value == 1 else 6
    item_pool += create_multiple_items(world, 'GLC PC Box Upgrade', upgrade_count, ItemClassification.useful)
    item_pool += create_multiple_items(world, 'Poke Cup PC Box Upgrade', upgrade_count, ItemClassification.useful)
    item_pool += create_multiple_items(world, 'Prime Cup PC Box Upgrade', upgrade_count, ItemClassification.useful)

    for name in bonus_pokemon_items:
        item_pool.append(create_item(world, name))

    # Place junk items
    item_pool += create_junk_items(world, get_total_locations(world) - len(item_pool) - 1)

    return item_pool

def create_item(world: 'PokemonStadiumWorld', name: str) -> Item:
    data = item_table[name]
    return PokemonStadiumItem(name, data.classification, data.ap_code, world.player)

def create_multiple_items(world: "PokemonStadiumWorld", name: str, count: int, item_type: ItemClassification = ItemClassification.progression) -> List[Item]:
    data = item_table[name]
    itemlist: List[Item] = []

    for _ in range(count):
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

cup_tier_upgrade_items = {
    'Poké Cup - Tier Upgrade': ItemData(10000017, ItemClassification.progression),
    'Prime Cup - Tier Upgrade': ItemData(10000018, ItemClassification.progression),
}

box_upgrade_items = {
    'GLC PC Box Upgrade': ItemData(10000101, ItemClassification.useful),
    'Poke Cup PC Box Upgrade' : ItemData(10000102, ItemClassification.useful),
    'Prime Cup PC Box Upgrade' : ItemData(10000103, ItemClassification.useful),
}

bonus_pokemon_items = {
    'Mewtwo': ItemData(10000201, ItemClassification.useful),
    'Mew': ItemData(10000202, ItemClassification.useful),
}

junk_items = {
    "Pokedoll": ItemData(10000200, ItemClassification.filler, 0),
}

junk_weights = {
    "Pokedoll": 40,
}

item_table = {
    **pokemon_stadium_items,
    **cup_tier_upgrade_items,
    **box_upgrade_items,
    **bonus_pokemon_items,
    **junk_items,
}
