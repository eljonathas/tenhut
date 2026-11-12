from __future__ import annotations

from tenhut.controllers import (
    AttentionController,
    BalloonTicker,
    ChatterController,
    ClickEffect,
    CountdownBeeper,
    Greeter,
    QuitController,
    RunState,
    SettingKey,
    SettingsController,
    SettingsRowCatalog,
    StatusReporter,
    Tickable,
    VolumePreviewEffect,
)
from tenhut.controllers.settings import CameraEnableGuard

from .ambient_controllers import AmbientControllers
from .camera_assembly import CameraAssembly
from .controller_groups import ControllerGroups
from .controller_parts import ControllerParts
from .core_assembly import CoreAssembly
from .core_controllers import CoreControllers
from .platform_parts import PlatformParts
from .rule_assembly import RuleAssembly
from .world_parts import WorldParts


class ControllerAssembly:
    """Creates every controller. The attention controller comes last on purpose: it draws the first random number
    after the scenery has drawn its own."""

    def __init__(self, platform: PlatformParts, world: WorldParts) -> None:
        self._platform = platform
        self._world = world

    def assemble(self) -> ControllerParts:
        platform, world = self._platform, self._world
        core = CoreAssembly(platform, world).assemble()
        rules = RuleAssembly(platform, world, core).assemble()
        camera = CameraAssembly(platform, world, core).assemble()
        ambient = AmbientControllers(self._chatter(core), self._attention(core))
        groups = ControllerGroups(core, rules, camera, ambient)
        run_state = RunState()
        return ControllerParts(
            core=core,
            rules=rules,
            camera=camera,
            settings=self._settings(groups),
            installer=rules.installer,
            attention=ambient.attention,
            reporter=self._reporter(groups),
            greeter=Greeter(world.session, core.speech),
            run_state=run_state,
            quitting=self._quitting(core, run_state),
            early_tickers=self._early(groups),
            late_tickers=self._late(core),
        )

    def _early(self, groups: ControllerGroups) -> tuple[Tickable, ...]:
        core, rules, camera, ambient = groups.core, groups.rules, groups.camera, groups.ambient
        return (
            rules.installer,
            rules.pomodoro,
            rules.judge,
            rules.blocking,
            camera.camera,
            camera.calibration,
            core.speech,
            ambient.chatter,
            ambient.attention,
            core.gestures,
        )

    def _late(self, core: CoreControllers) -> tuple[Tickable, ...]:
        beeper = CountdownBeeper(self._world.session, self._platform.clock, core.feedback)
        return core.feedback, beeper, BalloonTicker(self._world.balloon), core.navigator

    def _reporter(self, groups: ControllerGroups) -> StatusReporter:
        return StatusReporter(
            self._world.session,
            self._platform.settings,
            self._platform.clock,
            judge=groups.core.judge_slot,
            camera=groups.camera.camera,
            blocking=groups.rules.blocking_status,
        )

    def _quitting(self, core: CoreControllers, run_state: RunState) -> QuitController:
        world = self._world
        return QuitController(
            session=world.session,
            run_state=run_state,
            general=world.general,
            speech=core.speech,
            feedback=core.feedback,
            window=world.window,
        )

    def _settings(self, groups: ControllerGroups) -> SettingsController:
        platform, world = self._platform, self._world
        core, rules, camera = groups.core, groups.rules, groups.camera
        return SettingsController(
            active=platform.settings,
            store=platform.store,
            session=world.session,
            catalog=SettingsRowCatalog(platform.judge_factory, platform.paths.state_dir),
            sounds=world.sounds,
            speech=core.speech,
            feedback=core.feedback,
            navigation=core.navigator,
            judge=rules.judge,
            installer=rules.installer,
            calibration=camera.calibration,
            integration=platform.integration,
            guards={SettingKey.CAMERA_ENABLED: CameraEnableGuard(core.speech, camera.calibration)},
            effects={SettingKey.VOLUME: VolumePreviewEffect(world.sounds, core.feedback)},
            default_effect=ClickEffect(core.feedback),
        )

    def _chatter(self, core: CoreControllers) -> ChatterController:
        platform, world = self._platform, self._world
        return ChatterController(
            session=world.session,
            clock=platform.clock,
            speech=core.speech,
            navigation=core.navigator,
            judge=core.judge_slot,
            gestures=core.gestures,
            randomness=world.randomness,
            balloon=world.balloon,
        )

    def _attention(self, core: CoreControllers) -> AttentionController:
        platform, world = self._platform, self._world
        return AttentionController(
            general=world.general,
            balloon=world.balloon,
            session=world.session,
            clock=platform.clock,
            layouts=world.screen,
            speech=core.speech,
            feedback=core.feedback,
            navigation=core.navigator,
            judge=core.judge_slot,
            tracker=core.tracker,
            randomness=world.randomness,
        )
