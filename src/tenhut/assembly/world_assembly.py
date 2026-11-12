from __future__ import annotations

from tenhut.application_options import ApplicationOptions
from tenhut.core import ProfileStore, SessionStore
from tenhut.game.audio import SoundBank
from tenhut.game.character import Character
from tenhut.game.global_random import GlobalRandom
from tenhut.game.scenes import SceneRegistry
from tenhut.services.blocking import Blocker, HostsBackendFactory
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import LogicalScreen
from tenhut.ui.stage import DisplayWindow
from tenhut.ui.widgets import Balloon

from .platform_parts import PlatformParts
from .world_parts import WorldParts


class WorldAssembly:
    """Creates the window, the sounds, the general and the scenery. The general is created before the scenery:
    both draw from the same random stream and the order fixes what they look like."""

    def __init__(self, platform: PlatformParts, options: ApplicationOptions) -> None:
        self._platform = platform
        self._options = options

    def _blocker(self) -> Blocker:
        platform = self._platform
        backend = HostsBackendFactory(platform.runner, platform.clock).create(platform.system, self._options.dry_run)
        return Blocker(backend, platform.clock)

    def assemble(self) -> WorldParts:
        platform, settings = self._platform, self._platform.settings.current
        window = DisplayWindow(self._options.headless)
        fonts = FontSet()
        sounds = SoundBank(settings.sound.enabled and not self._options.headless, settings.sound.volume)
        balloon = Balloon(sounds)
        general = Character()
        scenes = SceneRegistry(platform.clock)
        return WorldParts(
            window=window,
            screen=LogicalScreen(fonts),
            fonts=fonts,
            sounds=sounds,
            balloon=balloon,
            general=general,
            scenes=scenes,
            blocker=self._blocker(),
            session=SessionStore(platform.paths.session_file, platform.clock).load(),
            profile=ProfileStore(platform.paths.profile_file).load(),
            randomness=GlobalRandom(),
        )
