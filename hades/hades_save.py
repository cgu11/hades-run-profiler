"""Data structures for individual runs / overall save data."""
from typing import Dict
from pathlib import Path

import pandas as pd
import json

from util.models.raw_save_file import RawSaveFile
from util.models.lua_state import LuaState


class HadesSave:
    """Contains data for an entire save file"""

    def __init__(self, filepath: Path):
        raw_save = RawSaveFile.from_file(filepath)
        self.save_dict = LuaState.from_bytes(
            version=raw_save.version, input_bytes=bytes(raw_save.lua_state_bytes)
        ).active_dict

        self.load_reference_dicts()
        self.create_run_df()

    def create_run_df(self):
        runs = self.save_dict["GameState"]["RunHistory"]

        self.runs = pd.DataFrame(
            columns=["index", "run_time", "run_complete", "aspect"]
        )

        for run_index, run_data in runs.items():
            index = int(run_index)
            run_time = run_data["GameplayTime"]
            run_complete = ("Cleared" in run_data.keys()) and (
                run_data["Cleared"] is True
            )
            aspect = self.get_aspect(run_data["WeaponsCache"], run_data["TraitCache"])
            self.runs.append([index, run_time, run_complete, aspect])

    def load_reference_dicts(self):
        with open("ref/boon_data.json") as f:
            self.boon_data = json.load(f)
        with open("ref/mirror_data.json") as f:
            self.mirror_data = json.load(f)
        with open("ref/pact_data.json") as f:
            self.pact_data = json.load(f)
        with open("ref/weapon_data.json") as f:
            self.weapon_data = json.load(f)

    def get_aspect(
        self, weapons_cache: Dict[str:str], trait_cache: Dict[str:int]
    ) -> str:
        weapons_traits = list(self.weapon_data.keys())
        cache_traits = list(weapons_cache.keys())
        other_traits = list(trait_cache.keys())

        for weapon in weapons_traits:
            if weapon in cache_traits:
                for aspect in weapons_traits[weapon]["AspectDict"].keys():
                    if aspect in other_traits:
                        return weapons_traits[weapon]["AspectDict"][aspect]

                return weapons_traits[weapon]["AspectDict"]["default"]

            raise ValueError(f"No weapon found. Run weapon traits: {cache_traits}")