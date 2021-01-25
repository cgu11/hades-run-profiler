"""Data structures for individual runs / overall save data."""

from pathlib import Path

import pandas as pd

from util.models.raw_save_file import RawSaveFile
from util.models.lua_state import LuaState


class HadesSave:
    """Contains data for an entire save file"""

    def __init__(self, filepath: Path):
        raw_save = RawSaveFile.from_file(filepath)
        self.save_dict = LuaState.from_bytes(
            version=raw_save.version, input_bytes=bytes(raw_save.lua_state_bytes)
        ).active_dict

        self.create_run_df()

    def create_run_df(self):
        runs = self.save_dict["GameState"]["RunHistory"]

        self.runs = pd.DataFrame(columns=["run_time", "run_complete"])

        for run_index, run_data in runs.items():
            pass
