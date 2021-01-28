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
        )._active_state

        self.load_reference_dicts()
        self.create_run_df()

    def create_run_df(self):
        runs = self.save_dict["GameState"]["RunHistory"]
        run_table = []

        for run_index, run_data in runs.items():
            index = int(run_index)
            run_time = run_data["GameplayTime"]
            run_complete = ("Cleared" in run_data.keys()) and (
                run_data["Cleared"] is True
            )
            weapon, aspect = self.get_weapon_aspect(
                run_data["WeaponsCache"], run_data["TraitCache"]
            )

            if run_complete:
                tunnel_count = self.get_tunnel_count(run_data["RoomCountCache"])
            else:
                tunnel_count = None

            run_table.append(
                {
                    "index": index,
                    "run_time": run_time,
                    "tunnel_count": tunnel_count,
                    "run_complete": run_complete,
                    "weapon": weapon,
                    "aspect": aspect,
                }
            )
        self.runs = pd.DataFrame(run_table)

    def load_reference_dicts(self):
        with open("ref/boon_data.json") as f:
            self.boon_data = json.load(f)
        with open("ref/mirror_data.json") as f:
            self.mirror_data = json.load(f)
        with open("ref/pact_data.json") as f:
            self.pact_data = json.load(f)
        with open("ref/weapon_data.json") as f:
            self.weapon_data = json.load(f)

    def get_weapon_aspect(
        self, weapons_cache: Dict[str, str], trait_cache: Dict[str, int]
    ) -> str:
        weapons_traits = list(self.weapon_data.keys())
        cache_traits = list(weapons_cache.keys())
        other_traits = list(trait_cache.keys())

        for weapon in weapons_traits:
            if weapon in cache_traits:
                for aspect in self.weapon_data[weapon]["AspectDict"].keys():
                    if aspect in other_traits:
                        return (
                            self.weapon_data[weapon]["DisplayName"],
                            self.weapon_data[weapon]["AspectDict"][aspect],
                        )

                return (
                    self.weapon_data[weapon]["DisplayName"],
                    self.weapon_data[weapon]["AspectDict"]["default"],
                )

        raise ValueError(f"No weapon found. Run weapon traits: {cache_traits}")

    def get_tunnel_count(self, room_count_cache: Dict) -> int:
        styx_miniboss_prefix = "D_MiniBoss"
        styx_combat_prefix = "D_Combat"

        tunnel_count = 0

        for room_id in room_count_cache.keys():
            if styx_miniboss_prefix in room_id or styx_combat_prefix in room_id:
                tunnel_count += 1

        # increment one for sack room
        return tunnel_count + 1
