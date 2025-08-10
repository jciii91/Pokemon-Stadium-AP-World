from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

from NetUtils import ClientStatus

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

class PokemonStadiumClient(BizHawkClient):
    game = "Pokemon Stadium"
    system = "N64"
    patch_suffix = ".apstadium"

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check ROM name
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0xB0, 15, "ROM")]))[0]).decode("ascii")
            if rom_name != "POKEMON STADIUM":
                return False
        except bizhawk.RequestFailedError:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            pass

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass
