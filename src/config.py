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

# オプションパラメータ
@dataclasses.dataclass
class OptionParam:
    min_val : int = None
    max_val : int = None
    value : int = None
    step : float = None

# プロファイルの設定
@dataclasses.dataclass
class Profile:
    # Option params
    volume : OptionParam = None
    speed : OptionParam = None
    pitch : OptionParam = None
    alpha : OptionParam = None
    intonation : OptionParam = None
    emotion : dict[str, OptionParam] = None

# ソフトウェア全体の設定
@dataclasses.dataclass
class SaveData:
    # Input params
    url : str = None
    file_path : str | os.PathLike = None
    seika_path : str | os.PathLike = None

    # Reader params
    voice : str = None
    chunk_size : int = None
    interval : float = None

    # Profiles
    profiles : dict[str, Profile] = None

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
        ret.step =      (base['step'] if 'step' in base else None)
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
            if 'profiles' in conf:
                if conf['profiles'] != None:
                    for profile in conf['profiles']:
                        print(profile)
                        self.data.profiles[profile].volume =    (self.dict2OptionParam(profile['volume']) if 'volume' in profile else None)
                        self.data.profiles[profile].speed =     (self.dict2OptionParam(profile['speed']) if 'speed' in profile else None)
                        self.data.profiles[profile].pitch =     (self.dict2OptionParam(profile['pitch']) if 'pitch' in profile else None)
                        self.data.profiles[profile].alpha =     (self.dict2OptionParam(profile['alpha']) if 'alpha' in profile else None)
                        self.data.profiles[profile].intonation =(self.dict2OptionParam(profile['intonation']) if 'intonation' in profile else None)
                        
                        if 'emotion' in profile:
                            for emo in profile['emotion']:
                                self.data.profiles[profile].emotion[emo] = self.dict2OptionParam(emo)
                        else:
                            self.data.profiles[profile].emotion = None
                else:
                    self.data.profiles = None
            elif self.data.voice != None:
                # Load old format profile
                self.data.profiles[self.data.voice].volume.min_val =    (conf['volume_min'] if 'volume_min' in conf else None)
                self.data.profiles[self.data.voice].volume.max_val =    (conf['volume_max'] if 'volume_max' in conf else None)
                self.data.profiles[self.data.voice].volume.value =      (conf['volume_val'] if 'volume_val' in conf else None)
                self.data.profiles[self.data.voice].volume.step =       (conf['volume_step'] if 'volume_step' in conf else None)
                self.data.profiles[self.data.voice].speed.min_val = (conf['speed_min'] if 'speed_min' in conf else None)
                self.data.profiles[self.data.voice].speed.max_val = (conf['speed_max'] if 'speed_max' in conf else None)
                self.data.profiles[self.data.voice].speed.value =   (conf['speed_val'] if 'speed_val' in conf else None)
                self.data.profiles[self.data.voice].speed.step =    (conf['speed_step'] if 'speed_step' in conf else None)

    def save_config(self, file_path="config.json"):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(self.data), f, ensure_ascii=False, indent=4)