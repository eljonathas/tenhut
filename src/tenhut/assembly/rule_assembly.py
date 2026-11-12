from __future__ import annotations

from tenhut.controllers import (
    AccessOutcome,
    BlockingController,
    BlockingStatus,
    CareerController,
    DesertionOutcome,
    HelperInstallController,
    JudgeController,
    MissionController,
    PomodoroController,
    RequestOutcome,
    SceneCelebration,
)
from tenhut.services.judge import RequestKind

from .core_controllers import CoreControllers
from .platform_parts import PlatformParts
from .rule_controllers import RuleControllers
from .world_parts import WorldParts


class RuleAssembly:
    """Creates the controllers that enforce the rules of the game."""

    def __init__(self, platform: PlatformParts, world: WorldParts, core: CoreControllers) -> None:
        self._platform = platform
        self._world = world
        self._core = core

    def assemble(self) -> RuleControllers:
        blocking = self._blocking()
        status = BlockingStatus(self._world.blocker, self._platform.system)
        career = CareerController(
            self._world.profile,
            self._core.feedback,
            self._core.speech,
            celebration=SceneCelebration(self._world.scenes),
        )
        mission = self._mission(blocking, status, career)
        return RuleControllers(
            blocking, status, career, mission, self._pomodoro(mission, career), self._judge(blocking), self._installer()
        )

    def _blocking(self) -> BlockingController:
        platform, world, core = self._platform, self._world, self._core
        return BlockingController(
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            blocker=world.blocker,
            killer=platform.killer,
            speech=core.speech,
            feedback=core.feedback,
            gestures=core.gestures,
        )

    def _mission(
        self, blocking: BlockingController, status: BlockingStatus, career: CareerController
    ) -> MissionController:
        platform, world, core = self._platform, self._world, self._core
        return MissionController(
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            navigation=core.navigator,
            speech=core.speech,
            feedback=core.feedback,
            blocking=status,
            enforcement=blocking,
            career=career,
            celebration=SceneCelebration(world.scenes),
            layouts=world.screen,
        )

    def _pomodoro(self, mission: MissionController, career: CareerController) -> PomodoroController:
        platform, world, core = self._platform, self._world, self._core
        return PomodoroController(
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            mission=mission,
            career=career,
            navigation=core.navigator,
            speech=core.speech,
            feedback=core.feedback,
        )

    def _outcomes(self) -> dict[RequestKind, RequestOutcome]:
        platform, world, core = self._platform, self._world, self._core
        shared = {
            "session": world.session,
            "settings": platform.settings,
            "speech": core.speech,
            "feedback": core.feedback,
            "gestures": core.gestures,
        }
        return {RequestKind.ACCESS: AccessOutcome(**shared), RequestKind.DESERTION: DesertionOutcome(**shared)}

    def _judge(self, blocking: BlockingController) -> JudgeController:
        platform, world, core = self._platform, self._world, self._core
        return JudgeController(
            slot=core.judge_slot,
            factory=platform.judge_factory,
            work_dir=platform.paths.state_dir,
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            log=platform.request_log,
            general=world.general,
            outcomes=self._outcomes(),
            speech=core.speech,
            feedback=core.feedback,
            navigation=core.navigator,
            enforcement=blocking,
        )

    def _installer(self) -> HelperInstallController:
        platform, world, core = self._platform, self._world, self._core
        return HelperInstallController(
            session=world.session,
            system=platform.system,
            runner=platform.runner,
            integration=platform.integration,
            blocker=world.blocker,
            speech=core.speech,
            feedback=core.feedback,
        )
