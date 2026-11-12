from __future__ import annotations

from tenhut.ui.stage import (
    AlertMark,
    FeedbackOverlay,
    FramePresenter,
    FrameRenderer,
    GeneralLayer,
    SceneStage,
    StageAnnouncer,
    StageTransitions,
    ThinkingDots,
    WhistleNotes,
)
from tenhut.ui.widgets import HudPlate, RankPlate

from .controller_parts import ControllerParts
from .platform_parts import PlatformParts
from .world_parts import WorldParts


class StageAssembly:
    """Creates the stage, with its overlays, and the renderer that draws every frame."""

    def __init__(self, platform: PlatformParts, world: WorldParts, controllers: ControllerParts) -> None:
        self._platform = platform
        self._world = world
        self._controllers = controllers

    def assemble(self) -> tuple[SceneStage, FrameRenderer]:
        transitions = self._transitions()
        stage = self._stage(transitions)
        return stage, self._renderer(stage, transitions)

    def _transitions(self) -> StageTransitions:
        platform, world, controllers = self._platform, self._world, self._controllers
        announcer = StageAnnouncer(world.session, controllers.feedback, controllers.speech)
        return StageTransitions(world.session, world.fonts, platform.clock, layouts=world.screen, listener=announcer)

    def _stage(self, transitions: StageTransitions) -> SceneStage:
        platform, world, controllers = self._platform, self._world, self._controllers
        layer = GeneralLayer(
            world.general,
            (AlertMark(world.general), WhistleNotes(world.general)),
            (ThinkingDots(controllers.judge_slot, platform.clock),),
        )
        return SceneStage(
            scenes=world.scenes,
            general=world.general,
            session=world.session,
            layouts=world.screen,
            gestures=controllers.gestures,
            transitions=transitions,
            general_layer=layer,
        )

    def _renderer(self, stage: SceneStage, transitions: StageTransitions) -> FrameRenderer:
        platform, world, controllers = self._platform, self._world, self._controllers
        presenter = FramePresenter(
            window=world.window, screen=world.screen, feedback=controllers.feedback, randomness=world.randomness
        )
        return FrameRenderer(
            stage=stage,
            transitions=transitions,
            presenter=presenter,
            screen=world.screen,
            navigator=controllers.navigator,
            balloon=world.balloon,
            gestures=controllers.gestures,
            session=world.session,
            blocking=controllers.blocking_status,
            overlay=FeedbackOverlay(controllers.feedback, world.screen, controllers.navigator),
            rank=RankPlate(world.profile),
            hud=HudPlate(world.session, platform.settings, platform.clock, reporter=controllers.reporter),
        )
