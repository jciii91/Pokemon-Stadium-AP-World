from worlds.generic.Rules import set_rule
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from . import PokemonStadiumWorld

def set_rules(world: "PokemonStadiumWorld"):
    player = world.player
    options = world.options

    # Gym Access
    gym_info_tuples = [
        ('Pewter', 'BROCK'),
        ('Cerulean', 'MISTY'),
        ('Vermillion', 'SURGE'),
        ('Celadon', 'ERIKA'),
        ('Fuchsia', 'KOGA'),
        ('Saffron', 'SABRINA'),
        ('Cinnabar', 'BLAINE'),
        ('Viridian', 'GIOVANNI'),
    ]

    if options.ProgressiveGLC.value == 1:
        set_glc_progressive_rules(world, player, gym_info_tuples)
    else:
        set_glc_base_rules(world, player, gym_info_tuples)

    # Cup Access
    set_cup_base_rules(world, player)

    #Trainersanity All
    if world.options.Trainersanity.value == 1:
        trainers = ['Bug Boy', 'Lad', 'Jr(M)']
        set_glc_trainersanity_rules(world, player, ('Pewter', 0), trainers)

        trainers = ['Fisher', 'Jr(F)', 'Swimmer']
        set_glc_trainersanity_rules(world, player, ('Cerulean', 1), trainers)

        trainers = ['Sailor', 'Rocker', 'Old Man']
        set_glc_trainersanity_rules(world, player, ('Vermillion', 2), trainers)

        trainers = ['Lass', 'Beauty', 'Cool(F)']
        set_glc_trainersanity_rules(world, player, ('Celadon', 3), trainers)

        trainers = ['Biker', 'Tamer', 'Juggler']
        set_glc_trainersanity_rules(world, player, ('Fuchsia', 4), trainers)

        trainers = ['Cue Ball', 'Burglar', 'Medium']
        set_glc_trainersanity_rules(world, player, ('Saffron', 5), trainers)

        trainers = ['Judoboy', 'Psychic', 'Nerd']
        set_glc_trainersanity_rules(world, player, ('Cinnabar', 6), trainers)

        trainers = ['Rocket', 'Lab Man', 'Cool(M)']
        set_glc_trainersanity_rules(world, player, ('Viridian', 7), trainers)

        trainers = ['Biker', 'Rocker', 'Juggler', 'Beauty', 'Medium', 'Tamer', 'Psychic', 'Old Man']
        set_cup_trainersanity_rules(world, player, 'Poké', trainers)

        trainers = ['Cue Ball', 'Rocket', 'Judoboy', 'Gambler', 'Cool(F)', 'Bird Boy', 'Lab Man', 'Cool(M)']
        set_cup_trainersanity_rules(world, player, 'Prime', trainers)

    # Beat Rival Rule
    badges = ["Boulder Badge", "Cascade Badge", "Thunder Badge", "Rainbow Badge", "Soul Badge", "Marsh Badge", "Volcano Badge", "Earth Badge"]
    badge_requirement = world.options.BadgeRequirement.value
    has_enough_badges = lambda state: state.has_from_list(badges, player, badge_requirement)
    set_rule(world.multiworld.get_location("Beat Rival", player), has_enough_badges)

    # Master Ball Cups Cleared Rule
    set_rule(
        world.multiworld.get_location("Master Ball Cups Cleared", player), 
        lambda state: state.count('Poké Cup - Tier Upgrade', player) > 2 and 
                      state.count('Prime Cup - Tier Upgrade', player) > 2
    )

    # Rival + Cups Rule
    set_rule(
        world.multiworld.get_location('Beat Rival and Clear Both Master Ball Cups', player),
        lambda state: state.has_from_list(badges, player, badge_requirement) and
                      state.count('Poké Cup - Tier Upgrade', player) > 2 and 
                      state.count('Prime Cup - Tier Upgrade', player) > 2
    )

    # Victory condition rule
    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)


def set_glc_base_rules(world: 'PokemonStadiumWorld', player: int, gym_info_tuples: List[Tuple[str, str]]):
    for gym_info in gym_info_tuples:
        gym = gym_info[0]
        leader = gym_info[1]
        location = f'{gym_info[0]} Gym'
        item = f'{gym} City Key' if gym != 'Cinnabar' else f'{gym} Island Key'
        set_rule(world.multiworld.get_location(location, player), lambda state: state.has(item, player))
        set_rule(world.multiworld.get_location(leader, player), lambda state: state.has(item, player))


def set_glc_progressive_rules(world: 'PokemonStadiumWorld', player: int, gym_info_tuples: List[Tuple[str, str]]):
    for i, gym_info in enumerate(gym_info_tuples):
        leader = gym_info[1]
        location = f'{gym_info[0]} Gym'
        item = 'Progressive Gym Key'
        set_rule(world.multiworld.get_location(location, player), lambda state: state.count(item, player) > i)
        set_rule(world.multiworld.get_location(leader, player), lambda state: state.count(item, player) > i)


def set_cup_base_rules(world: 'PokemonStadiumWorld', player: int):
    cups = ['Poké', 'Prime']
    tiers = ['Great', 'Ultra', 'Master']
    for cup in cups:
        item = f'{cup} Cup - Tier Upgrade'
        for i, tier in enumerate(tiers):
            location = f'{cup} Cup - {tier} Ball - Prize'
            set_rule(world.multiworld.get_location(location, player), lambda state: state.count(item, player) > i)

            # no Master Ball Cup - Tier Upgrade for Master tier, so only set rules for Great and Ultra tiers
            if i < 2:
                location = f'{cup} Cup - {tier} Ball - Tier Upgrade'
                set_rule(world.multiworld.get_location(location, player), lambda state: state.count(item, player) > i)


def set_glc_trainersanity_rules(world: 'PokemonStadiumWorld', player: int, gym_info: Tuple[str, str], trainers: List[str]):
    gym_name, gym_index = gym_info
    for i, trainer in enumerate(trainers):
        location = f'{gym_name} Gym - {trainer}'
        if world.options.ProgressiveGLC.value == 1:
            item = 'Progressive Gym Key'
            set_rule(world.multiworld.get_location(location, player), lambda state: state.count(item, player) > gym_index)
        else:
            item = f'{gym_name} City Key' if gym_name != 'Cinnabar' else f'{gym_name} Island Key'
            set_rule(world.multiworld.get_location(location, player), lambda state: state.has(item, player))


def set_cup_trainersanity_rules(world: 'PokemonStadiumWorld', player: int, cup_name: str, trainers: List[str]):
    tiers = ['Great', 'Ultra', 'Master']
    item = f'{cup_name} Cup - Tier Upgrade'
    for i, tier in enumerate(tiers):
        for trainer in trainers:
            location = f'{cup_name} Cup - {tier} Ball - {trainer}'
            set_rule(world.multiworld.get_location(location, player), lambda state: state.count(item, player) > i)
