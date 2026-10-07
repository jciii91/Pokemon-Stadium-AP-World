from copy import deepcopy
from random import Random
from typing import Sequence

from worlds.Files import APTokenTypes

from .constants import (
    kanto_dex_names,
    growth_rates,
    petit_cup_indexes,
    petitcupr1_levels,
    pikacupr1_levels,
    pika_cup_indexes,
    pokecupr1_master_levels,
    pokecupr1_ultra_levels,
    rom_offsets,
    vanilla_movesets,
    glc_difficulties,
    poke_cup_difficulties,
    prime_cup_difficulties,
    petit_cup_difficulties,
    pika_cup_difficulties,
)
from . import util
from .randomizePokemonBaseValues import BaseValuesRandomizer
from . import randomMovesetGenerator
from . import writeDisplayData

NOP = bytes([0x00,0x00,0x00,0x00])

class Randomizer():
    def __init__(
            self,
            seed=None,
            version="US_1.0",
            bst_factor=1, 
            trainer_factor=1,
            rental_factor=1,
            shuffle_factor=1,
        ):
        self.seed = seed
        self.random = Random(seed)

        self.version = version
        self.bst_factor = bst_factor
        self.trainer_factor = trainer_factor
        self.rental_factor = rental_factor
        self.shuffle_factor = shuffle_factor

        self.evs = []
        self.ivs = []
        for i in range(0, 151):
            if seed:
                seed = seed + str(i)

            self.evs.append(util.Util.random_int_set(0, 65535, 5, seed=seed))
            self.ivs.append(util.Util.random_string_hex(4, seed=seed))

        self.new_display_stats = []
        self.bst_list = []

        if(bst_factor == 1):
            for i in range(151):
                stats = kanto_dex_names[i]['bst']
                self.bst_list.append(stats)
                self.new_display_stats.append(stats)


    def disable_checksum(self, patch) -> None:
        offset = rom_offsets[self.version]["CheckSum1"]
        patch.write_token(APTokenTypes.WRITE, offset, NOP)

        offset = rom_offsets[self.version]["CheckSum2"]
        patch.write_token(APTokenTypes.WRITE, offset, NOP)


    def randomize_base_stats(self, patch) -> None:
        offset = rom_offsets[self.version]["BaseStats"]
        for i in range(151):
            stats = kanto_dex_names[i]['bst']
            if self.bst_factor > 1:
                randomized_base_stats = BaseValuesRandomizer.randomize_stats(stats, self.bst_factor, seed=self.seed)

                # Convert to list of integers for BST processing
                self.bst_list.append(list(randomized_base_stats))

                # Store modified stats for display
                self.new_display_stats.append(randomized_base_stats)

                # Write the new randomized stats back
                patch.write_token(APTokenTypes.WRITE, offset, bytes(randomized_base_stats))
            else:
                # store vanilla stats
                self.bst_list.append(stats)
                self.new_display_stats.append(stats)

            # Move to the next Pokémon entry (skip 18 additional bytes)
            offset += 23


    def write_pokemon_bytes(self, patch, external_offset, dex_index, pokemon, factor, level, location):
        offset = external_offset

        pokedex_num = dex_index + 1
        patch.write_token(APTokenTypes.WRITE, offset, bytes([pokedex_num]))  # Write Pokémon index
        offset += 1

        offset += 5  # Seek forward by 5 bytes

        new_type = bytes.fromhex(pokemon["type"])
        patch.write_token(APTokenTypes.WRITE, offset, bytes(new_type)) # Write Pokémon type
        offset += len(new_type)

        offset += 1  # Seek forward by 1 byte

        # Random moveset
        if "attacks" in pokemon:
            new_attacks = pokemon["attacks"]
        elif factor > 1 or location == "Trainer":
            bst = self.bst_list[dex_index]
            new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(sum(bst), seed=self.seed)
        else:
            new_attacks = vanilla_movesets[dex_index][location]

        for attack in new_attacks:
            patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
            offset += 1

        offset += 4  # Seek forward by 4 bytes

        growth_rate = pokemon["gr"]
        exp_for_level = growth_rates[growth_rate][level]
        exp = int.to_bytes(int(exp_for_level), 3, "big")
        patch.write_token(APTokenTypes.WRITE, offset, exp)
        offset += 3

        # Random EVs and IVs
        if factor > 1:
            for t in range(5):
                ev = int.to_bytes(self.evs[dex_index][t], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, ev)
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[dex_index])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)
        else:
            offset += 10

            int_set = [0, 0, 0, 0]
            iv_hex = ""
            for integer in int_set:
                iv_hex = iv_hex + hex(integer)[2:]
            ivs_bytes = bytes.fromhex(self.ivs[dex_index])
            offset += len(ivs_bytes)

        offset += 6  # Seek forward by 6 bytes

        new_stats = self.new_display_stats[dex_index]
        evs = self.evs[dex_index] if factor > 1 else [0, 0, 0, 0, 0]
        ivs = self.ivs[dex_index] if factor > 1 else "000000"
        disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(new_stats, evs, ivs, level)
        patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
        offset += len(disp)

        pokemon_name = pokemon["name"].encode()
        patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name))
        offset += len(pokemon_name)

        # Check if a Nidoran is being written in to add their gender symbol
        if pokedex_num == 29:
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("BE")) # Female symbol
            offset += 1
            pokemon_name += b" "
        elif pokedex_num == 32:
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("A9")) # Male symbol
            offset += 1
            pokemon_name += b" "

        # Fill in blank spaces to make the name 11 bytes long
        if len(pokemon_name) < 11:
            blanks = 11 - len(pokemon_name)
            patch.write_token(APTokenTypes.WRITE, offset, b"\x00" * blanks)
            offset += blanks

        return offset


    def get_pokemon_bytes(self, dex_index, pokemon, factor, level) -> Sequence[int]:
        pokemon_bytes = []

        pokedex_num = dex_index + 1
        pokemon_bytes.append(pokedex_num)
        pokemon_bytes.extend([0,0,0,level,0]) # Pad 5 bytes, write level

        new_type = bytes.fromhex(pokemon["type"])
        pokemon_bytes.extend(new_type)  # Pokémon type
        pokemon_bytes.extend([0])  # Pad 1 byte

        # Random moveset
        bst = self.bst_list[dex_index]
        new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(sum(bst), seed=self.seed)

        for attack in new_attacks:
            pokemon_bytes.append(attack)

        pokemon_bytes.extend([0,0,0,0])  # Pad 4 bytes

        growth_rate = pokemon["gr"]
        exp_for_level = growth_rates[growth_rate][level]
        exp = int.to_bytes(int(exp_for_level), 3, "big")
        pokemon_bytes.extend(exp)

        # Random EVs and IVs
        for t in range(5):
            ev = int.to_bytes(self.evs[dex_index][t], 2, "big")
            pokemon_bytes.extend(ev)

        ivs_bytes = bytes.fromhex(self.ivs[dex_index])
        pokemon_bytes.extend(ivs_bytes)
        pokemon_bytes.extend([0,0,0,0,level,0])  # Pad 6 bytes

        new_stats = self.new_display_stats[dex_index]
        evs = self.evs[dex_index] if factor > 0 else [0, 0, 0, 0, 0]
        ivs = self.ivs[dex_index] if factor > 0 else "000000"
        disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(new_stats, evs, ivs, level)
        pokemon_bytes.extend(disp)

        pokemon_name = pokemon["name"].encode()
        pokemon_bytes.extend(pokemon_name)

        # Fill in blank spaces to make the name 11 bytes long
        if len(pokemon_name) < 11:
            blanks = 11 - len(pokemon_name)
            pokemon_bytes.extend([0] * blanks)

        return pokemon_bytes

    def get_team_indexes(self, target_bst):
        target_sum = target_bst * 6
        all_indexes = list(range(149))
        bst_sums = {i: sum(kanto_dex_names[i]["bst"]) for i in all_indexes}

        best_team = None
        best_diff = None

        # Try many random teams and keep the one whose total BST is closest to the target.
        for _ in range(2500):
            team = self.random.sample(all_indexes, 6)
            team_sum = sum(bst_sums[index] for index in team)
            diff = abs(team_sum - target_sum)

            if best_team is None or diff < best_diff:
                best_team = team
                best_diff = diff
                if diff == 0:
                    break

        # Refine the best team with small swaps to improve the fit.
        team = list(best_team)
        for _ in range(1000):
            swap_index = self.random.randrange(6)
            candidate_index = self.random.randrange(149)

            if candidate_index in team:
                continue

            trial_team = team.copy()
            trial_team[swap_index] = candidate_index
            trial_sum = sum(bst_sums[index] for index in trial_team)
            trial_diff = abs(trial_sum - target_sum)

            if trial_diff < best_diff:
                team = trial_team
                best_diff = trial_diff
                if best_diff == 0:
                    break

        return team

    def randomize_glc_trainer_pokemon_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["GymCastle_Round1"]
        factor = self.trainer_factor
        difficulties_copy = list(glc_difficulties)

        if factor > 0:
            self.random.shuffle(difficulties_copy[:8])

        for q in range(10):
            bst_targets = difficulties_copy[q]
            for bst in bst_targets:
                new_team = list(self.get_team_indexes(bst))
                for dex_index in new_team:
                    pokemon = kanto_dex_names[dex_index]
                    level = 50
                    offset = self.write_pokemon_bytes(patch, offset, dex_index, pokemon, factor, level, "Trainer")

                    offset += 25  # Seek forward by 25 bytes
                offset += 56  # Seek forward by 56 bytes
            offset += 16  # Seek forward by 16 bytes


    def randomize_pokecup_trainer_pokemon_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["PokeCup_Round1"]
        factor = self.trainer_factor
        difficulties_copy = list(poke_cup_difficulties)

        if factor > 0:
            self.random.shuffle(difficulties_copy)

        for q in range(4):
            bst_targets = difficulties_copy[q]
            for i, bst in enumerate(bst_targets):
                new_team = list(self.get_team_indexes(bst))
                for j, dex_index in enumerate(new_team):
                    pokemon = kanto_dex_names[dex_index]

                    if q < 2:
                        level = 50 + q
                    elif q == 2:
                        level = pokecupr1_ultra_levels[i][j]
                    else:
                        level = pokecupr1_master_levels[i][j]

                    offset = self.write_pokemon_bytes(patch, offset, dex_index, pokemon, factor, level, "Trainer")

                    offset += 25  # Seek forward by 25 bytes
                offset += 56  # Seek forward by 56 bytes
            offset += 16  # Seek forward by 16 bytes


    def randomize_primecup_trainer_pokemon_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["PrimeCup_Round1"]
        factor = self.trainer_factor
        difficulties_copy = list(prime_cup_difficulties)

        if factor > 0:
            self.random.shuffle(difficulties_copy)

        for q in range(4):
            bst_targets = difficulties_copy[q]
            for bst in bst_targets:
                new_team = list(self.get_team_indexes(bst))
                for dex_index in new_team:
                    pokemon = kanto_dex_names[dex_index]
                    level = 100
                    offset = self.write_pokemon_bytes(patch, offset, dex_index, pokemon, factor, level, "Trainer")

                    offset += 25  # Seek forward by 25 bytes
                offset += 56  # Seek forward by 56 bytes
            offset += 16  # Seek forward by 16 bytes


    def randomize_petitcup_trainer_pokemon_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["PetitCup_Round1"]
        factor = self.trainer_factor
        difficulties_copy = list(petit_cup_difficulties)
        bst_targets = difficulties_copy[0]

        for i, bst in enumerate(bst_targets):
            new_team = list(self.get_team_indexes(bst))
            for j, dex_index in enumerate(new_team):
                pokemon = kanto_dex_names[dex_index]
                level = petitcupr1_levels[i][j]
                offset = self.write_pokemon_bytes(patch, offset, dex_index, pokemon, factor, level, "Trainer")

                offset += 25  # Seek forward by 25 bytes
            offset += 56  # Seek forward by 56 bytes
        offset += 16  # Seek forward by 16 bytes


    def randomize_pikacup_trainer_pokemon_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["PikaCup_Round1"]
        factor = self.trainer_factor
        difficulties_copy = list(pika_cup_difficulties)
        bst_targets = difficulties_copy[0]

        for i, bst in enumerate(bst_targets):
            new_team = list(self.get_team_indexes(bst))
            for j, dex_index in enumerate(new_team):
                pokemon = kanto_dex_names[dex_index]
                level = pikacupr1_levels[i][j]
                offset = self.write_pokemon_bytes(patch, offset, dex_index, pokemon, factor, level, "Trainer")

                offset += 25  # Seek forward by 25 bytes
            offset += 56  # Seek forward by 56 bytes
        offset += 16  # Seek forward by 16 bytes


    def randomize_glc_rentals_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["Rentals_GymCastle_Round1"] + 4
        factor = self.rental_factor
        kanto_dex_copy = deepcopy(kanto_dex_names[:149])

        for i, pokemon in enumerate(kanto_dex_copy):
            pokemon["index"] = i
            bst = sum(pokemon["bst"])
            pokemon["modified_bst"] = bst

            if factor > 0:
                new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(bst, seed=self.seed)
                pokemon["attacks"] = new_attacks
                pokemon["modified_bst"] = bst * (sum(modifiers) / 4)

        if self.shuffle_factor == 1:
            kanto_dex_copy.sort(key=lambda pokemon: pokemon["modified_bst"])
        elif self.shuffle_factor == 2:
            self.random.shuffle(kanto_dex_copy)

        for pokemon in kanto_dex_copy:
            offset = self.write_pokemon_bytes(patch, offset, pokemon["index"], pokemon, factor, 50, "GLC")
            offset += 25


    def randomize_pokecup_rentals(self, patch) -> None:
        offset = rom_offsets[self.version]["Rentals_PokeCup"] + 4
        factor = self.rental_factor
        kanto_dex_copy = deepcopy(kanto_dex_names[:149])

        for i, pokemon in enumerate(kanto_dex_copy):
            pokemon["index"] = i
            bst = sum(pokemon["bst"])
            pokemon["modified_bst"] = bst

            if factor > 0:
                new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(bst, seed=self.seed)
                pokemon["attacks"] = new_attacks
                pokemon["modified_bst"] = bst * (sum(modifiers) / 4)

        if self.shuffle_factor == 1:
            kanto_dex_copy.sort(key=lambda pokemon: pokemon["modified_bst"])
        elif self.shuffle_factor == 2:
            self.random.shuffle(kanto_dex_copy)

        for pokemon in kanto_dex_copy:
            offset = self.write_pokemon_bytes(patch, offset, pokemon["index"], pokemon, factor, 50, "PokeCup")
            offset += 25


    def randomize_primecup_rentals_round1(self, patch) -> None:
        offset = rom_offsets[self.version]["Rentals_PrimeCup_Round1"] + 4
        factor = self.rental_factor
        kanto_dex_copy = deepcopy(kanto_dex_names[:149])

        for i, pokemon in enumerate(kanto_dex_copy):
            pokemon["index"] = i
            bst = sum(pokemon["bst"])
            pokemon["modified_bst"] = bst

            if factor > 0:
                new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(bst, seed=self.seed)
                pokemon["attacks"] = new_attacks
                pokemon["modified_bst"] = bst * (sum(modifiers) / 4)

        if self.shuffle_factor == 1:
            kanto_dex_copy.sort(key=lambda pokemon: pokemon["modified_bst"])
        elif self.shuffle_factor == 2:
            self.random.shuffle(kanto_dex_copy)

        for pokemon in kanto_dex_copy:
            offset = self.write_pokemon_bytes(patch, offset, pokemon["index"], pokemon, factor, 100, "PrimeCup")
            offset += 25


    def randomize_petitcup_rentals(self, patch) -> None:
        offset = rom_offsets[self.version]["Rentals_PetitCup"] + 4
        factor = self.rental_factor
        kanto_dex_copy = deepcopy(kanto_dex_names[:149])

        for i, pokemon in enumerate(kanto_dex_copy):
            pokemon["index"] = i
            bst = sum(pokemon["bst"])
            pokemon["modified_bst"] = bst

            if factor > 0:
                new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(bst, seed=self.seed)
                pokemon["attacks"] = new_attacks
                pokemon["modified_bst"] = bst * (sum(modifiers) / 4)

        if self.shuffle_factor == 1:
            kanto_dex_copy.sort(key=lambda pokemon: pokemon["modified_bst"])

        for pokemon in kanto_dex_copy:
            if pokemon["index"] not in petit_cup_indexes:
                continue

            offset = self.write_pokemon_bytes(patch, offset, pokemon["index"], pokemon, factor, 25, "PetitCup")
            offset += 25


    def randomize_pikacup_rentals(self, patch) -> None:
        offset = rom_offsets[self.version]["Rentals_PikaCup"] + 4
        factor = self.rental_factor
        kanto_dex_copy = deepcopy(kanto_dex_names[:149])

        for i, pokemon in enumerate(kanto_dex_copy):
            pokemon["index"] = i
            bst = sum(pokemon["bst"])
            pokemon["modified_bst"] = bst

            if factor > 0:
                new_attacks, modifiers = randomMovesetGenerator.MovesetGenerator.get_random_moveset_and_modifiers(bst, seed=self.seed)
                pokemon["attacks"] = new_attacks
                pokemon["modified_bst"] = bst * (sum(modifiers) / 4)

        if self.shuffle_factor == 1:
            kanto_dex_copy.sort(key=lambda pokemon: pokemon["modified_bst"])

        for pokemon in kanto_dex_copy:
            if pokemon["index"] not in pika_cup_indexes:
                continue

            offset = self.write_pokemon_bytes(patch, offset, pokemon["index"], pokemon, factor, 15, "PikaCup")
            offset += 25
