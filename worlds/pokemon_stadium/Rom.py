import hashlib
import os

from settings import get_settings
import subprocess
from worlds.AutoWorld import World
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes

import Utils

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
    # Bypass CIC
    patch.write_token(APTokenTypes.WRITE, 0x63C, NOP)
    patch.write_token(APTokenTypes.WRITE, 0x648, NOP)

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
