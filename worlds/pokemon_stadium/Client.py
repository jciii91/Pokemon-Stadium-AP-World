import logging
from typing import TYPE_CHECKING

from .Items import pokemon_stadium_items, gym_badge_codes
from .Locations import pokemon_stadium_locations, event_locations
from NetUtils import ClientStatus
from .Types import LocData
import Utils
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

logger = logging.getLogger('Client')

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

class PokemonStadiumClient(BizHawkClient):
    game = 'Pokemon Stadium'
    system = 'N64'
    patch_suffix = '.apstadium'

    def __init__(self):
        super().__init__()

        self.local_checked_locations = set()
        self.glc_loaded = False
        self.minigame_index = None

    async def validate_rom(self, ctx: 'BizHawkClientContext') -> bool:
        try:
            # Check ROM name
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x20, 15, 'ROM')]))[0]).decode('ascii')
            if rom_name != 'POKEMON STADIUM':
                logger.info('Invalid ROM for Pokemon Stadium AP World')
                return False
        except bizhawk.RequestFailedError:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True

        return True

    async def game_watcher(self, ctx: 'BizHawkClientContext') -> None:
        item_codes = {net_item.item for net_item in ctx.items_received}

        flags = await bizhawk.read(ctx.bizhawk_ctx, [
                (0x420000, 4, 'RDRAM'), # GLC Flag
                (0x420010, 4, 'RDRAM'), # Entered Battle Flag
                (0x148AC8, 12, 'RDRAM'), # Beat Rival Flag
                (0x12FC1C, 4, 'RDRAM'), # Minigame being played
                (0x124860, 4, 'RDRAM'), # Minigame results
            ]
        )

        glc_flag = int.from_bytes(flags[0], byteorder='big')
        if glc_flag == 2 and not self.glc_loaded:
            self.glc_loaded = True

            battle_info = await bizhawk.read(ctx.bizhawk_ctx, [(0x0AE540, 4, 'RDRAM')])
            gym_number = battle_info[0].hex()[4:]
            player_has_battled = flags[1] != b'\x00\x00\x00\x00'

            if player_has_battled:
                gym_locations = {
                    '0004': set([pokemon_stadium_locations['Pewter Gym'].ap_code, pokemon_stadium_locations['BROCK'].ap_code]),
                    '0104': set([pokemon_stadium_locations['Cerulean Gym'].ap_code, pokemon_stadium_locations['MISTY'].ap_code]),
                    '0204': set([pokemon_stadium_locations['Vermillion Gym'].ap_code, pokemon_stadium_locations['SURGE'].ap_code]),
                    '0304': set([pokemon_stadium_locations['Celadon Gym'].ap_code, pokemon_stadium_locations['ERIKA'].ap_code]),
                    '0404': set([pokemon_stadium_locations['Fuchsia Gym'].ap_code, pokemon_stadium_locations['KOGA'].ap_code]),
                    '0504': set([pokemon_stadium_locations['Saffron Gym'].ap_code, pokemon_stadium_locations['SABRINA'].ap_code]),
                    '0604': set([pokemon_stadium_locations['Cinnabar Gym'].ap_code, pokemon_stadium_locations['BLAINE'].ap_code]),
                    '0704': set([pokemon_stadium_locations['Viridian Gym'].ap_code, pokemon_stadium_locations['GIOVANNI'].ap_code]),
                    '0901': set([event_locations['Beat Rival'].ap_code]),
                }

                try:
                    await ctx.check_locations(gym_locations[gym_number])
                    await bizhawk.write(ctx.bizhawk_ctx, [(0x420010, [0x00, 0x00, 0x00, 0x00], 'RDRAM')])
                    self.glc_loaded = False
                except:
                    pass

            self.GLC_UNLOCK_FLAGS = [
                0x147B70, # Pewter
                0x147B98, # Cerulean
                0x147BC0, # Vermilion
                0x147BE8, # Celadon
                0x147C10, # Fuchsia
                0x147C38, # Saffron
                0x147C60, # Cinnabar
                0x147C88, # Viridian
                0x147CB1, # E4 entrance
                0x147CD9, # E4 exit
                0x147D01, # E4
            ]

            # UUDDLLRR
            self.GLC_CURSOR_TARGETS = [
                0x147B84, # Brock,       00000002
                0x147BAC, # Misty,       03000103
                0x147BD4, # Surge,       04020200
                0x147BFC, # Erika,       05030500
                0x147C24, # Koga,        06040604
                0x147C4C, # Sabrina,     07050007
                0x147C74, # Blaine,      00080608
                0x147C9C, # Giovanni,    07000709
            ]

            gym_codes = [
                pokemon_stadium_items['Pewter City Key'].ap_code,
                pokemon_stadium_items['Cerulean City Key'].ap_code,
                pokemon_stadium_items['Vermillion City Key'].ap_code,
                pokemon_stadium_items['Celadon City Key'].ap_code,
                pokemon_stadium_items['Fuchsia City Key'].ap_code,
                pokemon_stadium_items['Saffron City Key'].ap_code,
                pokemon_stadium_items['Cinnabar Island Key'].ap_code,
                pokemon_stadium_items['Viridian City Key'].ap_code,
            ]

            self.unlocked_gyms = [i + 1 for i, code in enumerate(gym_codes) if code in item_codes]
            victory_road_open = set(gym_badge_codes).issubset(item_codes)
            if victory_road_open:
                self.unlocked_gyms.append(9)

            if gym_codes[0] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[0], [0x00, 0x01], 'RDRAM')])
                await self.update_brock_cursor(ctx)

            if gym_codes[1] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[1], [0x00, 0x01], 'RDRAM')])
                await self.update_misty_cursor(ctx)

            if gym_codes[2] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[2], [0x00, 0x01], 'RDRAM')])
                await self.update_surge_cursor(ctx)

            if gym_codes[3] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[3], [0x00, 0x01], 'RDRAM')])
                await self.update_erika_cursor(ctx)

            if gym_codes[4] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[4], [0x00, 0x01], 'RDRAM')])
                await self.update_koga_cursor(ctx)

            if gym_codes[5] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[5], [0x00, 0x01], 'RDRAM')])
                await self.update_sabrina_cursor(ctx)

            if gym_codes[6] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[6], [0x00, 0x01], 'RDRAM')])
                await self.update_blaine_cursor(ctx)

            if gym_codes[7] in item_codes:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[7], [0x00, 0x01], 'RDRAM')])
                await self.update_giovanni_cursor(ctx, item_codes)

            if victory_road_open:
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[8], [0x01], 'RDRAM')])
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[9], [0x01], 'RDRAM')])
                await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_UNLOCK_FLAGS[10], [0x01], 'RDRAM')])

            if len(self.unlocked_gyms) > 0 and gym_number != '0804':
                first_gym = self.unlocked_gyms[0] - 1
                await bizhawk.write(ctx.bizhawk_ctx, [(0x147D50, [0x00, first_gym], 'RDRAM')])

            await bizhawk.write(ctx.bizhawk_ctx, [(0x146F38, [0x52, 0x61, 0xFF, 0x82], 'RDRAM')])

        elif glc_flag != 2 and self.glc_loaded:
            self.glc_loaded = False

        text = flags[2].decode("ascii", errors="ignore")
        if text == 'Magnificent!':
            await ctx.check_locations(set([event_locations['Beat Rival'].ap_code]))
            await bizhawk.write(ctx.bizhawk_ctx, [(0x420010, [0x00, 0x00, 0x00, 0x00], 'RDRAM')])

        # Send game clear
        if not ctx.finished_game and pokemon_stadium_items['Victory'].ap_code in item_codes:
            ctx.finished_game = True
            await ctx.send_msgs([{
                "cmd": "StatusUpdate",
                "status": ClientStatus.CLIENT_GOAL,
            }])

        # Minigames
        if flags[3].startswith(b'\x00\x03\x00') and flags[3][3] in range(9):
            self.minigame_index = flags[3][3]

            await bizhawk.write(ctx.bizhawk_ctx, [(0x124860, [0x00, 0x00, 0x00, 0x00], 'RDRAM')])

        if self.minigame_index != None and flags[4] == b'\x01\x00\x00\x00':
            minigame_ap_acode = 20000100 + self.minigame_index
            await ctx.check_locations([minigame_ap_acode])
            self.minigame_index = None

    def lowest_unlocked_from(self, lower_bound):
        for i in range(lower_bound, 9):
            if i in self.unlocked_gyms:
                return i
        return 0

    def highest_unlocked_from(self, upper_bound):
        for i in range(upper_bound, 0, -1):
            if i in self.unlocked_gyms:
                return i
        return 0

    async def update_brock_cursor(self, ctx):
        # Determine UP: lowest unlocked gym from 4 to 9
        up = self.lowest_unlocked_from(4)

        # Determine RIGHT: lowest of 2 or 3 or 4 if any are unlocked
        right = 0
        misty_unlocked = 2 in self.unlocked_gyms
        surge_unlocked = 3 in self.unlocked_gyms
        erika_unlocked = 4 in self.unlocked_gyms

        if misty_unlocked:
            right = 2
        elif surge_unlocked:
            right = 3
        elif erika_unlocked:
            right = 4

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[0], [up, 0x00, 0x00, right], 'RDRAM')])

    async def update_misty_cursor(self, ctx):
        # Determine UP: lowest unlocked gym from 4 to 9
        up = self.lowest_unlocked_from(4)

        # Determine LEFT: is Brock unlocked
        left = 1 if 1 in self.unlocked_gyms else 0

        # Determine RIGHT: is Surge unlocked
        right = 3 if 3 in self.unlocked_gyms else 0

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[1], [up, 0x00, left, right], 'RDRAM')])

    async def update_surge_cursor(self, ctx):
        # Determine UP: lowest unlocked gym from 4 to 9
        up = self.lowest_unlocked_from(4)

        # Determine DOWN: is Misty unlocked
        down = 2 if 2 in self.unlocked_gyms else 0

        # Determine LEFT: is Misty or Brock unlocked
        left = 0
        misty_unlocked = 2 if 2 in self.unlocked_gyms else 0
        brock_unlocked = 1 if 1 in self.unlocked_gyms else 0

        if misty_unlocked:
            left = 2
        elif brock_unlocked:
            left = 1

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[2], [up, down, left, 0x00], 'RDRAM')])

    async def update_erika_cursor(self, ctx):
        # Determine UP: lowest unlocked gym from 5 to 9
        up = self.lowest_unlocked_from(5)

        # Determine DOWN: highest unlocked gym from 3 to 1
        down = self.highest_unlocked_from(3)

        # Determine LEFT: is Koga or Sabrina unlocked
        left = 0
        koga_unlocked = 5 if 5 in self.unlocked_gyms else 0
        sabrina_unlocked = 6 if 6 in self.unlocked_gyms else 0

        if koga_unlocked: 
            left = 5
        elif sabrina_unlocked:
            left = 6

        # Determine RIGHT: is Surge unlocked
        right = 3 if 3 in self.unlocked_gyms else 0

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[3], [up, down, left, right], 'RDRAM')])

    async def update_koga_cursor(self, ctx):
        # Determine UP: lowest unlocked gym from 6 to 9
        up = self.lowest_unlocked_from(6)

        # Determine DOWN: highest unlocked gym from 2 to 1
        down = self.highest_unlocked_from(2)

        # Determine LEFT: is Sabrina unlocked
        left = 6 if 6 in self.unlocked_gyms else 0

        # Determine RIGHT: is Erika or Surge unlocked
        right = 0
        erika_unlocked = 4 if 4 in self.unlocked_gyms else 0
        surge_unlocked = 3 if 3 in self.unlocked_gyms else 0

        if erika_unlocked:
            right = 4
        elif surge_unlocked:
            right = 3

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[4], [up, down, left, right], 'RDRAM')])

    async def update_sabrina_cursor(self, ctx):
        # Determine DOWN: highest unlocked gym from 5 to 1
        down = self.highest_unlocked_from(5)

        # Determine RIGHT: is Blaine or Giovanni unlocked
        right = 0
        blaine_unlocked = 7 if 7 in self.unlocked_gyms else 0
        giovanni_unlocked = 8 if 8 in self.unlocked_gyms else 0

        if blaine_unlocked:
            right = 7
        elif giovanni_unlocked:
            right = 8

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[5], [0x00, down, 0x00, right], 'RDRAM')])

    async def update_blaine_cursor(self, ctx):
        # Determine DOWN: highest unlocked gym from 5 to 1
        down = self.highest_unlocked_from(5)

        # Determine LEFT: is Sabrina unlocked
        left = 6 if 6 in self.unlocked_gyms else 0

        # Determine RIGHT: is Giovanni unlocked
        right = 8 if 8 in self.unlocked_gyms else 0

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[6], [0x00, down, left, right], 'RDRAM')])

    async def update_giovanni_cursor(self, ctx, item_codes):
        # Determine UP: All badges obtained?
        up = 9 if set(gym_badge_codes).issubset(item_codes) else 0

        # Determine DOWN: highest unlocked gym from 5 to 1
        down = self.highest_unlocked_from(5)

        # Determine LEFT: is Blaine or Sabrina unlocked
        left = 0
        blaine_unlocked = 7 if 7 in self.unlocked_gyms else 0
        sabrina_unlocked = 6 if 6 in self.unlocked_gyms else 0

        if blaine_unlocked:
            left = 7
        elif sabrina_unlocked:
            left = 6

        # Determine RIGHT: All badges obtained?
        right = up

        await bizhawk.write(ctx.bizhawk_ctx, [(self.GLC_CURSOR_TARGETS[7], [up, down, left, right], 'RDRAM')])
