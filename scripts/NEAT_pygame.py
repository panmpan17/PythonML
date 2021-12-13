from .utilities import ProgressBar
from .pygame_foundation import ManagedWindow, Vector


class NEATManagedWindow(ManagedWindow):
    def __init__(self, run_pygame, size: Vector, tick_limit=False) -> None:
        super().__init__(size, step_update=False, tick=30, tick_limit=tick_limit)

        self.run_pygame = run_pygame

        self.progress_bar: ProgressBar = None

        self.last_high_score = 0
        self.round_since_last_high_score = 0

        self.total_round = 0
        self.generation_count = 0
        self.generation_round_count = 0

    def update_high_score(self, new_score):
        if new_score > self.last_high_score:
            self.last_high_score = new_score
            self.round_since_last_high_score = 0
        else:
            self.round_since_last_high_score += 1

    def reset(self):
        pass

    def run_without_pygame(self):
        pass

    def start(self):
        if self.run_pygame:
            self.run()
        else:
            self.run_without_pygame()
