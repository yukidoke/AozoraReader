"""
This file is part of AozoraReader.

AozoraReader is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

AozoraReader is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with AozoraReader. If not, see <https://www.gnu.org/licenses/>.
"""

import dataclasses
import json
import os
from collections import defaultdict
import copy

# オプションパラメータ
@dataclasses.dataclass
class OptionParam:
    min_val : int = None
    max_val : int = None
    value : int = None
    scale : float = None

    def set_value(self, min : int, max : int, value : int, scale : float):
        self.min_val = min
        self.max_val = max
        self.value = value
        self.scale = scale

# ソフトウェア全体の設定
@dataclasses.dataclass
class SaveData:
    # Input params
    url : str = None
    file_path : str | os.PathLike = None
    seika_path : str | os.PathLike = None

    # Reader params
    voice : str = None
    chunk_size : int = 100
    interval : float = 0.5

    # Profiles
    effect : dict[str, dict[str, OptionParam]] = dataclasses.field(default_factory=lambda: defaultdict(lambda: defaultdict(OptionParam)))
    emotion : dict[str, dict[str, OptionParam]] = dataclasses.field(default_factory=lambda: defaultdict(lambda: defaultdict(OptionParam)))

# 設定データを管理するクラス
class DataManager:
    def __init__(self):
        """
        AssistantSeikaの設定を管理するクラス
        """
        self.data = SaveData()

    def dict2OptionParam(self, base : dict):
        ret = OptionParam()
        ret.min_val =   (base['min_val'] if 'min_val' in base else None)
        ret.max_val =   (base['max_val'] if 'max_val' in base else None)
        ret.value =     (base['value'] if 'value' in base else None)
        ret.scale =      (base['step'] if 'step' in base else None)
        return ret

    def load_config(self, file_path="config.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            conf = json.load(f)

            # Load data
            self.data.url =         (conf['url'] if 'url' in conf else None)
            self.data.file_path =   (conf['file_path'] if 'file_path' in conf else None)
            self.data.seika_path =  (conf['seika_path'] if 'seika_path' in conf else "C:/Program Files/510Product/AssistantSeika")
            self.data.voice =       (conf['voice'] if 'voice' in conf else None)
            self.data.chunk_size =  (conf['chunk_size'] if 'chunk_size' in conf else 100)
            self.data.interval =    (conf['interval'] if 'interval' in conf else 0.5)

            # Load profile
            if 'effect' in conf:
                for profile in conf['effect']:
                    for param in conf['effect'][profile]:
                        self.data.effect[profile][param] = self.dict2OptionParam(conf['effect'][profile][param])

            elif self.data.voice != None:
                # Load old format profile
                self.data.effect[self.data.voice]['volume'].set_value(conf['volume_min'], conf['volume_max'], conf['volume_val'], conf['volume_step'])
                self.data.effect[self.data.voice]['speed'].set_value(conf['speed_min'], conf['speed_max'], conf['speed_val'], conf['speed_step'])

            if 'emotion' in conf:
                for profile in conf['emotion']:
                    for param in conf['emotion'][profile]:
                        self.data.emotion[profile][param] = self.dict2OptionParam(conf['emotion'][profile][param])

    def save_config(self, file_path="config.json"):
        with open(file_path, "w", encoding="utf-8") as f:
            effects = {}
            for voice in self.data.effect:
                effects[voice] = {}
                for param in self.data.effect[voice]:
                    effects[voice][param] = dataclasses.asdict(self.data.effect[voice][param])
            emotions = {}
            for voice in self.data.emotion:
                emotions[voice] = {}
                for param in self.data.emotion[voice]:
                    emotions[voice][param] = dataclasses.asdict(self.data.emotion[voice][param])

            j : json = {}
            j['url'] = self.data.url
            j['file_path'] = self.data.file_path
            j['seika_path'] = self.data.seika_path
            j['voice'] = self.data.voice
            j['chunk_size'] = self.data.chunk_size
            j['interval'] = self.data.interval
            j['effect'] = json.loads(json.dumps(effects, ensure_ascii=False, indent=4))
            j['emotion'] = json.loads(json.dumps(emotions, ensure_ascii=False, indent=4))
            json.dump(j, f, ensure_ascii=False, indent=4)