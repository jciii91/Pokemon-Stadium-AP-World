import hashlib
import os

from settings import get_settings
import Utils
from worlds.AutoWorld import World
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes

from .randomizer import stadium_randomizer

NOP = bytes([0x00,0x00,0x00,0x00])
MD5Hash = "ed1378bc12115f71209a77844965ba50"

class PokemonStadiumProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon Stadium"
    hash = MD5Hash
    patch_file_ending = ".apstadium"
    result_file_ending = ".z64"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()

def get_base_rom_bytes() -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path()
        base_rom_bytes = bytes(Utils.read_snes_rom(open(file_name, "rb")))

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        md5hash = basemd5.hexdigest()
        if MD5Hash !=md5hash:
            raise Exception("Supplied Rom does not match known MD5 for Pokemon Stadium")
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes

def get_base_rom_path():
    file_name = get_settings()["stadium_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name

def write_tokens(world:World, patch:PokemonStadiumProcedurePatch):
    # version = settings['ROMVersion']
    bst_factor = world.options.BaseStatTotalRandomness.value
    glc_trainer_factor = world.options.GymCastleTrainerRandomness.value
    glc_rental_factor = world.options.GymCastleRentalRandomness.value
    pokecup_rental_factor = world.options.PokeCupRentalRandomness.value
    primecup_rental_factor = world.options.PrimeCupRentalRandomness.value
    petitcup_rental_factor = world.options.PetitCupRentalRandomness.value
    pikacup_rental_factor = world.options.PikaCupRentalRandomness.value
    rental_list_shuffle_factor = world.options.RentalListShuffle.value
    rental_list_shuffle_glc_factor = world.options.RentalListShuffleGLC.value
    rental_list_shuffle_poke__cup_factor = world.options.RentalListShufflePokeCup.value
    rental_list_shuffle_prime_cup_factor = world.options.RentalListShufflePrimeCup.value
    rental_list_shuffle_petit_cup_factor = world.options.RentalListShufflePetitCup.value
    rental_list_shuffle_pika_cup_factor = world.options.RentalListShufflePikaCup.value
    rom_bytes = get_base_rom_bytes()
    randomizer = stadium_randomizer.Randomizer('US_1.0', bst_factor, glc_trainer_factor, glc_rental_factor, pokecup_rental_factor, primecup_rental_factor,
                                               petitcup_rental_factor, pikacup_rental_factor, rental_list_shuffle_factor, rental_list_shuffle_glc_factor, rental_list_shuffle_poke__cup_factor,
                                               rental_list_shuffle_prime_cup_factor, rental_list_shuffle_petit_cup_factor,
                                               rental_list_shuffle_pika_cup_factor, rom_bytes)

    # Bypass CIC
    randomizer.disable_checksum(patch)
    if bst_factor > 1:
        randomizer.randomize_base_stats(patch)
    if glc_trainer_factor > 1:
        randomizer.randomize_glc_trainer_pokemon_round1(patch)
    if glc_rental_factor > 1:
        randomizer.randomize_glc_rentals_round1(patch)
    if pokecup_rental_factor > 1:
        randomizer.randomize_pokecup_rentals(patch)
    if primecup_rental_factor > 1:
        randomizer.randomize_primecup_rentals_round1(patch)
    if petitcup_rental_factor > 1:
        randomizer.randomize_petitcup_rentals(patch)
    if pikacup_rental_factor > 1:
        randomizer.randomize_pikacup_rentals(patch)
    if rental_list_shuffle_factor > 1:
        if rental_list_shuffle_factor != 3: #Not in manual mode
            randomizer.shuffle_rentals(patch)
        else:
            if rental_list_shuffle_glc_factor > 1:
                randomizer.shuffle_glc(patch)
            if rental_list_shuffle_poke__cup_factor > 1:
                randomizer.shuffle_poke(patch)
            if rental_list_shuffle_prime_cup_factor > 1:
                randomizer.shuffle_prime(patch)
            if rental_list_shuffle_petit_cup_factor > 1:
                randomizer.shuffle_petit(patch)
            if rental_list_shuffle_poke__cup_factor > 1:
                randomizer.shuffle_poke(patch)


    # Set GP Register to 80420000
    patch.write_token(APTokenTypes.WRITE, 0x202B8, bytes([0x3C, 0x1C, 0x80, 0x42]))

    # Set 'Entering Gym' flag
    patch.write_token(APTokenTypes.WRITE, 0x2C520, bytes([0xAF, 0x81, 0x00, 0x10]))

    # Clear 'Entering Gym' flag
    patch.write_token(APTokenTypes.WRITE, 0x396D08, bytes([0xAF, 0x80, 0x00, 0x10]))

    # Turn off A and B button on GLC select screen
    patch.write_token(APTokenTypes.WRITE, 0x3B4DA8, bytes([0x50, 0x21, 0xFF, 0x82]))

    # First instruction to set flag for GLC selection screen
    patch.write_token(APTokenTypes.WRITE, 0x3B5548, bytes([0xAF, 0x84, 0x00, 0x00]))

    # Second instruction to set flag for GLC selection screen
    patch.write_token(APTokenTypes.WRITE, 0x3B55F4, bytes([0xAF, 0x82, 0x00, 0x00]))

    # Stop game from activating unlocked gyms
    patch.write_token(APTokenTypes.WRITE, 0x3B5728, bytes([0xA3, 0x20, 0x00, 0x01]))

    # Write patch file
    patch.write_file("token_data.bin", patch.get_token_binary())
