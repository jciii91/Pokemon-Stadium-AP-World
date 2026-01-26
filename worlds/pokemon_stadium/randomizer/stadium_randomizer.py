import random

from worlds.Files import APTokenTypes

from . import constants
from . import util
from .randomizePokemonBaseValues import BaseValuesRandomizer
from . import randomMovesetGenerator
from . import writeDisplayData

NOP = bytes([0x00,0x00,0x00,0x00])

class Randomizer():
    def __init__(self, version="US_1.0", bst_factor=1, glc_trainer_factor=1, glc_rental_factor=1, 
                  pokecup_rental_factor=1, primecup_rental_factor=1, petitcup_rental_factor=1, pikacup_rental_factor=1,rental_list_shuffle_factor=1,
                 rls_glc_factor=1, rls_poke_factor=1, rls_prime_factor=1, rls_petit_factor=1,
                 rls_pika_factor=1, rom_bytes=0x00):
        self.version = version
        self.bst_factor = bst_factor
        self.glc_trainer_factor = glc_trainer_factor
        self.glc_rental_factor = glc_rental_factor
        self.pokecup_rental_factor = pokecup_rental_factor
        self.primecup_rental_factor = primecup_rental_factor
        self.petitcup_rental_factor = petitcup_rental_factor
        self.rental_list_shuffle_factor = rental_list_shuffle_factor
        self.pikacup_rental_factor = pikacup_rental_factor
        self.rls_glc_factor = rls_glc_factor
        self.rls_poke_factor = rls_poke_factor
        self.rls_prime_factor = rls_prime_factor
        self.rls_petit_factor = rls_petit_factor
        self.rls_pika_factor = rls_pika_factor
        self.rom_bytes = rom_bytes

        self.evs = []
        self.ivs = []
        for _ in range(0, 149):
            self.evs.append(util.Util.random_int_set(0, 65535, 5))
            self.ivs.append(util.Util.random_string_hex(4))

        self.new_display_stats = []
        self.bst_list = []

        # store vanilla stats
        if(bst_factor == 1):
            for i in range(149):
                stats = constants.kanto_dex_names[i]['bst']
                self.bst_list.append(stats)
                self.new_display_stats.append(stats)

    def disable_checksum(self, patch) -> None:
        offset = constants.rom_offsets[self.version]["CheckSum1"]
        patch.write_token(APTokenTypes.WRITE, offset, NOP)

        offset = constants.rom_offsets[self.version]["CheckSum2"]
        patch.write_token(APTokenTypes.WRITE, offset, NOP)

    def randomize_base_stats(self, patch) -> None:
        offset = constants.rom_offsets[self.version]["BaseStats"]
        for i in range(149):
            stats = constants.kanto_dex_names[i]['bst']
            randomized_base_stats = BaseValuesRandomizer.randomize_stats(stats, self.bst_factor)

            # Convert to list of integers for BST processing
            self.bst_list.append(list(randomized_base_stats))

            # Store modified stats for display
            self.new_display_stats.append(randomized_base_stats)

            # Write the new randomized stats back
            patch.write_token(APTokenTypes.WRITE, offset, bytes(randomized_base_stats))
            # # store vanilla stats
            # self.bst_list.append(stats)
            # self.new_display_stats.append(stats)

            # Move to the next Pokémon entry (skip 18 additional bytes)
            offset += 23

    def randomize_glc_trainer_pokemon_round1(self, patch) -> None:
        factor = self.glc_trainer_factor
        offset = constants.rom_offsets[self.version]["GymCastle_Round1"]
        for q in range(10):
            team_count = 4 if q < 9 else 7
            for _ in range(team_count):
                new_team = random.sample(range(149), 6)
                for s in range(6):
                    pokedex_num = new_team[s]
                    patch.write_token(APTokenTypes.WRITE, offset, bytes([pokedex_num + 1]))  # Write Pokémon index
                    offset += 1

                    offset += 5  # Seek forward by 5 bytes

                    new_type = bytes.fromhex(constants.kanto_dex_names[pokedex_num]["type"])
                    patch.write_token(APTokenTypes.WRITE, offset, bytes(new_type)) # Write Pokémon type
                    offset += len(new_type)

                    offset += 1  # Seek forward by 1 byte

                    # Random moveset
                    bst = self.bst_list[pokedex_num]
                    
                    new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst, factor, new_type)
                    for attack in new_attacks:
                        patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                        offset += 1

                    offset += 4  # Seek forward by 4 bytes

                    exp = int.to_bytes(int(constants.kanto_dex_names[pokedex_num]["exp"]), 3, "big")
                    patch.write_token(APTokenTypes.WRITE, offset, exp)
                    offset += 3

                    for t in range(5):
                        ev = int.to_bytes(self.evs[pokedex_num][t], 2, "big")
                        patch.write_token(APTokenTypes.WRITE, offset, ev)
                        offset += 2

                    ivs_bytes = bytes.fromhex(self.ivs[pokedex_num])
                    patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
                    offset += len(ivs_bytes)

                    offset += 6  # Seek forward by 6 bytes

                    new_stats = self.new_display_stats[pokedex_num]
                    evs = self.evs[pokedex_num]
                    ivs = self.ivs[pokedex_num]
                    disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(new_stats, evs, ivs, 50)
                    patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
                    offset += len(disp)

                    pokemon_name = constants.kanto_dex_names[pokedex_num]["name"].encode()
                    patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name))
                    offset += len(pokemon_name)

                    # Check if a Nidoran is being written in to add their gender symbol
                    if pokedex_num == 28:
                        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("BE")) # Female symbol
                        offset += 1
                        pokemon_name += b" "
                    elif pokedex_num == 31:
                        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("BE")) # Male symbol
                        offset += 1
                        pokemon_name += b" "

                    # Fill in blank spaces to make the name 11 bytes long
                    if len(pokemon_name) < 11:
                        blanks = 11 - len(pokemon_name)
                        patch.write_token(APTokenTypes.WRITE, offset, b"\x00" * blanks)
                        offset += blanks

                    offset += 25  # Seek forward by 25 bytes
                offset += 56  # Seek forward by 56 bytes
            offset += 16  # Seek forward by 16 bytes

    def randomize_glc_rentals_round1(self, patch) -> None:
        #randomize rentals for GLC
        offset = constants.rom_offsets[self.version]["Rentals_GymCastle_Round1"]
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes([j + 1])) # Write Dex number
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0008")) # Current HP
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("32")) # Level

            offset += 1
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00")) # Status
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pkm_type)) # Type(s)
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            # Random moveset
            bst_list = self.bst_list[j]
            factor = self.glc_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("1110")) # Trainer ID
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            patch.write_token(APTokenTypes.WRITE, offset, bytes(exp_bytes)) # Experience
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("32")) # Level again
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 50)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name)) # Name
            offset += 11

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("52414E444F000000")) # Trainer name (RANDO)
            offset += 8

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000000000000000000000000000000000")) # Padding
            offset += 17
            
    def randomize_pokecup_rentals(self, patch) -> None:
        #randomize pokemon in Poke Cup rental list
        offset = constants.rom_offsets[self.version]["Rentals_PokeCup"]
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes([j + 1])) # Write Dex number
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0008")) # Current HP
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("32")) # Level
            offset += 1
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00")) # Status
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pkm_type)) # Type(s)
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            # Random moveset
            bst_list = self.bst_list[j]
            factor = self.pokecup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("1110")) # Trainer ID
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            patch.write_token(APTokenTypes.WRITE, offset, bytes(exp_bytes)) # Experience
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("32")) # Level again
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 50)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name)) # Name
            offset += 11

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("52414E444F000000")) # Trainer name (RANDO)
            offset += 8

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000000000000000000000000000000000")) # Padding
            offset += 17
    def randomize_primecup_rentals_round1(self, patch) -> None:
        #randomize pokemon in Poke Cup rental list
        offset = constants.rom_offsets[self.version]["Rentals_PrimeCup_Round1"]
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes([j + 1])) # Write Dex number
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0008")) # Current HP
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("64")) # Level
            offset += 1
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00")) # Status
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pkm_type)) # Type(s)
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            # Random moveset
            bst_list = self.bst_list[j]
            factor = self.primecup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("1110")) # Trainer ID
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            patch.write_token(APTokenTypes.WRITE, offset, bytes(exp_bytes)) # Experience
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("64")) # Level again
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 100)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name)) # Name
            offset += 11

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("52414E444F000000")) # Trainer name (RANDO)
            offset += 8

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000000000000000000000000000000000")) # Padding
            offset += 17
    def randomize_petitcup_rentals(self, patch) -> None:
        #randomize pokemon in Petit Cup rental list
        offset = constants.rom_offsets[self.version]["Rentals_PetitCup"]
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000002D"))
        offset += 4

        for j in range(45):
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes([constants.petit_cup_list[j]["DexNum"]])) # Write Dex number
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0008")) # Current HP
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("19")) # Level
            offset += 1
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00")) # Status
            offset += 1

            pkm_type = bytes.fromhex(constants.petit_cup_list[j]["type"])
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pkm_type)) # Type(s)
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            # Random moveset
            bst_list = constants.petit_cup_list[j]["bst"]
            factor = self.petitcup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("1110")) # Trainer ID
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.petit_cup_list[j]["exp"]), 3, "big")
            patch.write_token(APTokenTypes.WRITE, offset, bytes(exp_bytes)) # Experience
            offset += 3

            currentPokeDexNum = constants.petit_cup_list[j]["DexNum"]
            for k in range(5):
                ev = int.to_bytes(self.evs[currentPokeDexNum][k], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[currentPokeDexNum])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("19")) # Level again
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[currentPokeDexNum]
            evs = self.evs[currentPokeDexNum]
            ivs = self.ivs[currentPokeDexNum]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 25)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
            offset += len(disp)

            pokemon_name = constants.petit_cup_list[j]["name"].encode().ljust(11, b'\x00')
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name)) # Name
            offset += 11

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("52414E444F000000")) # Trainer name (RANDO)
            offset += 8

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000000000000000000000000000000000")) # Padding
            offset += 17
    def randomize_pikacup_rentals(self, patch) -> None:
    #randomize pokemon in Pika Cup rental list
        offset = constants.rom_offsets[self.version]["Rentals_PikaCup"]
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000005B"))
        offset += 4

        for j in range(91):
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes([constants.pika_cup_list[j]["DexNum"]])) # Write Dex number
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0008")) # Current HP
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0F")) # Level
            offset += 1
            
            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00")) # Status
            offset += 1

            pkm_type = bytes.fromhex(constants.pika_cup_list[j]["type"])
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pkm_type)) # Type(s)
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            # Random moveset
            bst_list = constants.pika_cup_list[j]["bst"]
            factor = self.pikacup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                patch.write_token(APTokenTypes.WRITE, offset, bytes([attack]))
                offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("1110")) # Trainer ID
            offset += 2

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.pika_cup_list[j]["exp"]), 3, "big")
            patch.write_token(APTokenTypes.WRITE, offset, bytes(exp_bytes)) # Experience
            offset += 3

            currentPokeDexNum = constants.pika_cup_list[j]["DexNum"]
            for k in range(5):
                ev = int.to_bytes(self.evs[currentPokeDexNum][k], 2, "big")
                patch.write_token(APTokenTypes.WRITE, offset, bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[currentPokeDexNum])
            patch.write_token(APTokenTypes.WRITE, offset, ivs_bytes)
            offset += len(ivs_bytes)

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0F")) # Level again
            offset += 1

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[currentPokeDexNum]
            evs = self.evs[currentPokeDexNum]
            ivs = self.ivs[currentPokeDexNum]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 15)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(disp))
            offset += len(disp)

            pokemon_name = constants.pika_cup_list[j]["name"].encode().ljust(11, b'\x00')
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_name)) # Name
            offset += 11

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("52414E444F000000")) # Trainer name (RANDO)
            offset += 8

            patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000000000000000000000000000000000")) # Padding
            offset += 17
    def shuffle_rentals(self, patch) -> None:
        #Shuffle time
        self.shuffle_glc(patch)
        self.shuffle_poke(patch)
        self.shuffle_prime(patch)
        self.shuffle_petit(patch)
        self.shuffle_pika(patch)
        return patch

        
    def shuffle_glc(self, patch) -> None:
        #Gym Leader Castle
        #Shuffle GLC Rental Table
        offset = constants.rom_offsets[self.version]["Rentals_GymCastle_Round1"]
        
        pokemon_holder = []
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            current_pokemon_bytearray = bytearray()
            
            current_pokemon_bytearray.extend(bytes([j + 1]))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("0008"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("32"))
            offset += 1
            
            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            current_pokemon_bytearray.extend(bytes(pkm_type))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            # I don't know how to check the bytes in the rom for the current moveset
            bst_list = self.bst_list[j]
            factor = self.glc_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                current_pokemon_bytearray.extend(bytes([attack]))
                offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("1110"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            current_pokemon_bytearray.extend(bytes(exp_bytes))
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                current_pokemon_bytearray.extend(bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            current_pokemon_bytearray.extend(ivs_bytes)
            offset += len(ivs_bytes)

            current_pokemon_bytearray.extend(bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            current_pokemon_bytearray.extend(bytes.fromhex("32"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 50)
            current_pokemon_bytearray.extend(bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            current_pokemon_bytearray.extend(bytes(pokemon_name))
            offset += 11

            current_pokemon_bytearray.extend(bytes.fromhex("52414E444F000000"))
            offset += 8

            current_pokemon_bytearray.extend(bytes.fromhex("0000000000000000000000000000000000"))
            offset += 17


            pokemon_holder.append(bytearray(current_pokemon_bytearray))
            
        #Shuffles order of rental pokemon
        random.shuffle(pokemon_holder)

        offset = constants.rom_offsets[self.version]["Rentals_GymCastle_Round1"]

        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

    
        while len(pokemon_holder) > 0:
            #Get pokemon bytes from list
            pokemon_to_add = pokemon_holder.pop(0)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_to_add))
            offset+= len(bytes(pokemon_to_add))
        print("GLC rentals shuffled successfully")
    def shuffle_poke(self, patch) -> None:
        #Poke Cup
        #Shuffle Poke Cup Rental Table
        offset = constants.rom_offsets[self.version]["Rentals_PokeCup"]
        
        pokemon_holder = []
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            current_pokemon_bytearray = bytearray()
            
            current_pokemon_bytearray.extend(bytes([j + 1]))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("0008"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("32"))
            offset += 1
            
            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            current_pokemon_bytearray.extend(bytes(pkm_type))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            # I don't know how to check the bytes in the rom for the current moveset
            bst_list = self.bst_list[j]
            factor = self.pokecup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                current_pokemon_bytearray.extend(bytes([attack]))
                offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("1110"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            current_pokemon_bytearray.extend(bytes(exp_bytes))
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                current_pokemon_bytearray.extend(bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            current_pokemon_bytearray.extend(ivs_bytes)
            offset += len(ivs_bytes)

            current_pokemon_bytearray.extend(bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            current_pokemon_bytearray.extend(bytes.fromhex("32"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 50)
            current_pokemon_bytearray.extend(bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            current_pokemon_bytearray.extend(bytes(pokemon_name))
            offset += 11

            current_pokemon_bytearray.extend(bytes.fromhex("52414E444F000000"))
            offset += 8

            current_pokemon_bytearray.extend(bytes.fromhex("0000000000000000000000000000000000"))
            offset += 17


            pokemon_holder.append(bytearray(current_pokemon_bytearray))
            
        #Shuffles order of rental pokemon
        random.shuffle(pokemon_holder)

        offset = constants.rom_offsets[self.version]["Rentals_PokeCup"]

        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

    
        while len(pokemon_holder) > 0:
            #Get pokemon bytes from list
            pokemon_to_add = pokemon_holder.pop(0)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_to_add))
            offset+= len(bytes(pokemon_to_add))
        print("Poke Cup rentals shuffled successfully")
    def shuffle_prime(self, patch) -> None:
        #Prime Cup
        #Shuffle Prime Cup Rental Table
        offset = constants.rom_offsets[self.version]["Rentals_PrimeCup_Round1"]
        
        pokemon_holder = []
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

        for j in range(149):
            current_pokemon_bytearray = bytearray()
            
            current_pokemon_bytearray.extend(bytes([j + 1]))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("0008"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("64"))
            offset += 1
            
            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            pkm_type = bytes.fromhex(constants.kanto_dex_names[j]["type"])
            current_pokemon_bytearray.extend(bytes(pkm_type))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            # I don't know how to check the bytes in the rom for the current moveset
            bst_list = self.bst_list[j]
            factor = self.primecup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                current_pokemon_bytearray.extend(bytes([attack]))
                offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("1110"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.kanto_dex_names[j]["exp"]), 3, "big")
            current_pokemon_bytearray.extend(bytes(exp_bytes))
            offset += 3

            for k in range(5):
                ev = int.to_bytes(self.evs[j][k], 2, "big")
                current_pokemon_bytearray.extend(bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[j])
            current_pokemon_bytearray.extend(ivs_bytes)
            offset += len(ivs_bytes)

            current_pokemon_bytearray.extend(bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            current_pokemon_bytearray.extend(bytes.fromhex("64"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[j]
            evs = self.evs[j]
            ivs = self.ivs[j]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 100)
            current_pokemon_bytearray.extend(bytes(disp))
            offset += len(disp)

            pokemon_name = constants.kanto_dex_names[j]["name"].encode().ljust(11, b'\x00')
            current_pokemon_bytearray.extend(bytes(pokemon_name))
            offset += 11

            current_pokemon_bytearray.extend(bytes.fromhex("52414E444F000000"))
            offset += 8

            current_pokemon_bytearray.extend(bytes.fromhex("0000000000000000000000000000000000"))
            offset += 17


            pokemon_holder.append(bytearray(current_pokemon_bytearray))
            
        #Shuffles order of rental pokemon
        random.shuffle(pokemon_holder)

        offset = constants.rom_offsets[self.version]["Rentals_PrimeCup_Round1"]

        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("00000095"))
        offset += 4

    
        while len(pokemon_holder) > 0:
            #Get pokemon bytes from list
            pokemon_to_add = pokemon_holder.pop(0)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_to_add))
            offset+= len(bytes(pokemon_to_add))
        print("Prime Cup rentals shuffled successfully")
    def shuffle_petit(self, patch) -> None:
        #Petit Cup
        #Shuffle Petit Cup Rental Table
        offset = constants.rom_offsets[self.version]["Rentals_PetitCup"]
        
        pokemon_holder = []
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000002D"))
        offset += 4

        for j in range(45):
            current_pokemon_bytearray = bytearray()
            
            current_pokemon_bytearray.extend(bytes([constants.petit_cup_list[j]["DexNum"]]))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("0008"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("19"))
            offset += 1
            
            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            pkm_type = bytes.fromhex(constants.petit_cup_list[j]["type"])
            current_pokemon_bytearray.extend(bytes(pkm_type))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            # I don't know how to check the bytes in the rom for the current moveset
            bst_list = constants.petit_cup_list[j]["bst"]
            factor = self.petitcup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                current_pokemon_bytearray.extend(bytes([attack]))
                offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("1110"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.petit_cup_list[j]["exp"]), 3, "big")
            current_pokemon_bytearray.extend(bytes(exp_bytes))
            offset += 3
            currentPokeDexNum = constants.petit_cup_list[j]["DexNum"]
            for k in range(5):
                ev = int.to_bytes(self.evs[currentPokeDexNum][k], 2, "big")
                current_pokemon_bytearray.extend(bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[currentPokeDexNum])
            current_pokemon_bytearray.extend(ivs_bytes)
            offset += len(ivs_bytes)

            current_pokemon_bytearray.extend(bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            current_pokemon_bytearray.extend(bytes.fromhex("19"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[currentPokeDexNum]
            evs = self.evs[currentPokeDexNum]
            ivs = self.ivs[currentPokeDexNum]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 25)
            current_pokemon_bytearray.extend(bytes(disp))
            offset += len(disp)

            pokemon_name = constants.petit_cup_list[j]["name"].encode().ljust(11, b'\x00')
            current_pokemon_bytearray.extend(bytes(pokemon_name))
            offset += 11

            current_pokemon_bytearray.extend(bytes.fromhex("52414E444F000000"))
            offset += 8

            current_pokemon_bytearray.extend(bytes.fromhex("0000000000000000000000000000000000"))
            offset += 17


            pokemon_holder.append(bytearray(current_pokemon_bytearray))
            
        #Shuffles order of rental pokemon
        random.shuffle(pokemon_holder)

        offset = constants.rom_offsets[self.version]["Rentals_PetitCup"]

        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000002D"))
        offset += 4

    
        while len(pokemon_holder) > 0:
            #Get pokemon bytes from list
            pokemon_to_add = pokemon_holder.pop(0)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_to_add))
            offset+= len(bytes(pokemon_to_add))
        print("Petit Cup rentals shuffled successfully")
    def shuffle_pika(self, patch) -> None:
        #Pika Cup
        #Shuffle Pika Cup Rental Table
        offset = constants.rom_offsets[self.version]["Rentals_PikaCup"]
         
        pokemon_holder = []
        
        # Write expected number of returned Pokémon
        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000005B"))
        offset += 4

        for j in range(91):
            current_pokemon_bytearray = bytearray()
            
            current_pokemon_bytearray.extend(bytes([constants.pika_cup_list[j]["DexNum"]]))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("0008"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("0F"))
            offset += 1
            
            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            pkm_type = bytes.fromhex(constants.pika_cup_list[j]["type"])
            current_pokemon_bytearray.extend(bytes(pkm_type))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            # I don't know how to check the bytes in the rom for the current moveset
            bst_list = constants.pika_cup_list[j]["bst"]
            factor = self.pikacup_rental_factor
            new_attacks = randomMovesetGenerator.MovesetGenerator.get_random_moveset(bst_list, factor, pkm_type)
            for attack in new_attacks:
                current_pokemon_bytearray.extend(bytes([attack]))
                offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("1110"))
            offset += 2

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            exp_bytes = int.to_bytes(int(constants.pika_cup_list[j]["exp"]), 3, "big")
            current_pokemon_bytearray.extend(bytes(exp_bytes))
            offset += 3
            currentPokeDexNum = constants.pika_cup_list[j]["DexNum"]
            for k in range(5):
                ev = int.to_bytes(self.evs[currentPokeDexNum][k], 2, "big")
                current_pokemon_bytearray.extend(bytes(ev))
                offset += 2

            ivs_bytes = bytes.fromhex(self.ivs[currentPokeDexNum])
            current_pokemon_bytearray.extend(ivs_bytes)
            offset += len(ivs_bytes)

            current_pokemon_bytearray.extend(bytes.fromhex("00000000"))
            offset += 4  # I think setting these to 0 gives you the vanilla PP for moves

            current_pokemon_bytearray.extend(bytes.fromhex("0F"))
            offset += 1

            current_pokemon_bytearray.extend(bytes.fromhex("00"))
            offset += 1

            stats = self.new_display_stats[currentPokeDexNum]
            evs = self.evs[currentPokeDexNum]
            ivs = self.ivs[currentPokeDexNum]
            disp = writeDisplayData.DisplayDataWriter.write_gym_tower_display(stats, evs, ivs, 15)
            current_pokemon_bytearray.extend(bytes(disp))
            offset += len(disp)

            pokemon_name = constants.pika_cup_list[j]["name"].encode().ljust(11, b'\x00')
            current_pokemon_bytearray.extend(bytes(pokemon_name))
            offset += 11

            current_pokemon_bytearray.extend(bytes.fromhex("52414E444F000000"))
            offset += 8

            current_pokemon_bytearray.extend(bytes.fromhex("0000000000000000000000000000000000"))
            offset += 17


            pokemon_holder.append(bytearray(current_pokemon_bytearray))
            
        #Shuffles order of rental pokemon
        random.shuffle(pokemon_holder)

        offset = constants.rom_offsets[self.version]["Rentals_PikaCup"]

        patch.write_token(APTokenTypes.WRITE, offset, bytes.fromhex("0000005B"))
        offset += 4

    
        while len(pokemon_holder) > 0:
            #Get pokemon bytes from list
            pokemon_to_add = pokemon_holder.pop(0)
            patch.write_token(APTokenTypes.WRITE, offset, bytes(pokemon_to_add))
            offset+= len(bytes(pokemon_to_add))
        print("Pika Cup rentals shuffled successfully")
    
        





