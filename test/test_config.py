import pytest
import json
import os
from src.config import Config, DataManager, SaveData, OptionParam
from collections import defaultdict
from pathlib import Path

@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def config():
    return Config()

@pytest.mark.parametrize("file_path, expected", [
    ("null.json", FileNotFoundError),
    ("ng001.json", json.JSONDecodeError),
    ("ok001.json", {"t_bool": False,"t_float": 2.3,"t_array": ["yuki","aozora","seika"]})
])
def test_config_path_to_data(file_path : str, expected, fixtures_dir : Path, config):
    """
    テストの意図: config.jsonのパスが与えられたとき、それを読み取ってpython objectのデータに変換することを確認する。
    仕様:
        - ファイルが存在しないとき、FileNotFoundErrorを返す
        - ファイルが存在するとき、json to python objを実行する
        - json to python objに失敗したとき、json.JSONDecodeErrorを返す。
    """
    assert config.path_to_data(fixtures_dir / file_path) == expected

@pytest.mark.parametrize("file_name, expected", [
    ("v1.0.0_01.json",({"url": "https://www.aozora.gr.jp/cards/000879/files/127_15260.html","file_path": "D:/sandbox/AozoraReader/クソデカ羅生門.txt","seika_path": "D:\\sandbox\\AozoraReader\\assistantseika20250113a\\SeikaSay2","voice": "すずきつづみ  - CeVIOAI(64)","chunk_size": 100,"interval": 1.0,"effect": {},"emotion": {}},False)),
    ("v2.0.0_01.json",({"config_version": "v2.1.0","url": "https://www.aozora.gr.jp/cards/000081/files/456_15050.html","file_path": "D:/sandbox/AozoraReader/クソデカ羅生門.txt","main_voice": None,"sub_voice": None,"chunk_size": 100,"interval": 0.0,"parameters": {},"http_settings": {"address": "localhost","port": 7180,"basic_userid": "SeikaServerUser","basec_password": "SeikaServerPassword"}},True)),
    ("v2.1.0_01.json",({"config_version": "v2.1.0","url": "https://www.aozora.gr.jp/cards/000081/files/456_15050.html","file_path": "test","main_voice": "60011","sub_voice": "70021","chunk_size": 101,"interval": 1.0,"parameters": {"60011": {"effect": {"volume": {"value": 1,"min": 0.0,"max": 2.0,"step": 0.01},"speed": {"value": 1,"min": 0.10,"max": 5.0,"step": 0.01},"pitch": {"value": 1,"min": 0.10,"max": 5.0,"step": 0.01},"intonation": {"value": 1,"min": 0.0,"max": 5.0,"step": 0.01},"shortpause": {"value": 150,"min": 80.0,"max": 500.0,"step": 1.00},"longpause": {"value": 370,"min": 80.0,"max": 2000.0,"step": 1.00}},"emotion": {"喜び": {"value": 0,"min": 0.00,"max": 1.00,"step": 0.01},"怒り": {"value": 0,"min": 0.00,"max": 1.00,"step": 0.01},"悲しみ": {"value": 0,"min": 0.00,"max": 1.00,"step": 0.01}}},"70021": {"effect": {"volume": {"min_val": 0,"max_val": 100,"value": 50,"scale": 1.0},"speed": {"min_val": 0,"max_val": 100,"value": 65,"scale": 1.0},"pitch": {"min_val": 0,"max_val": 100,"value": 50,"scale": 1.0},"alpha": {"min_val": 0,"max_val": 100,"value": 50,"scale": 1.0},"intonation": {"min_val": 0,"max_val": 100,"value": 50,"scale": 1.0}},"emotion": {"クール": {"min_val": 0,"max_val": 100,"value": 50,"scale": 1.0},"照れ": {"min_val": 0,"max_val": 100,"value": 0,"scale": 1.0},"怒り": {"min_val": 0,"max_val": 100,"value": 0,"scale": 1.0},"喜び": {"min_val": 0,"max_val": 100,"value": 30,"scale": 1.0},"ひそひそ": {"min_val": 0,"max_val": 100,"value": 0,"scale": 1.0}}}},"http_settings": {"address": "192.168.0.1","port": 8080,"basic_userid": "admin","basec_password": "pass"}},True)),
    ("invalid_01.json",({"config_version": "v2.1.0","url": None,"file_path": None,"main_voice": None,"sub_voice": None,"chunk_size": 100,"interval": 1.0,"parameters": {},"http_settings": {"address": "localhost","port": 7180,"basic_userid": "SeikaServerUser","basec_password": "SeikaServerPassword"}}, True))
])
def test_config_update_data_version(file_name : str, expected, fixtures_dir : Path, config):
    """
    テストの意図: configデータが渡されたとき、最新バージョンのconfig形式に変換されることを確認する。
    仕様:
        - python objectとして渡されたデータが最新バージョンでないなら一つ新しいバージョンに変換する。
        - 戻り値は(data, latest)であり、変換後データが最新形式ならlatest=Trueとなる。
        - v2.1.0以前のデータは話者が一意に特定できないため、話者ごとのデータはデフォルトデータとする。
        - データ形式が無効ならデフォルトデータを返す。
    """
    with open(fixtures_dir / "config" / file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert config.update_data_version(data) == expected

@pytest.fixture
def data_manager():
    """DataManagerのインスタンスを作成するfixture"""
    return DataManager()

@pytest.fixture
def test_config_file(tmpdir):
    """テスト用のconfig.jsonファイルを作成するfixture"""
    config_data = {
        "url": "http://example.com",
        "file_path": "test.txt",
        "seika_path": "C:/Seika",
        "voice": "voice1",
        "chunk_size": 200,
        "interval": 1.0,
        "effect": {
            "voice1": {
                "volume": {"min_val": 0, "max_val": 100, "value": 50, "step": 1},
                "speed": {"min_val": 50, "max_val": 150, "value": 100, "step": 5},
            }
        },
        "emotion": {
            "voice1": {
                "happy": {"min_val": 0, "max_val": 100, "value": 75, "step": 1},
            }
        },
    }
    config_file = tmpdir.join("config.json")
    config_file.write(json.dumps(config_data))
    return str(config_file)

def test_option_param_init():
    """OptionParamが正しく初期化されることをテスト"""
    param = OptionParam()
    assert param.min_val is None
    assert param.max_val is None
    assert param.value is None
    assert param.scale is None

def test_option_param_set_value():
    """OptionParamのset_valueメソッドが正しく値を設定できることをテスト"""
    param = OptionParam()
    param.set_value(1, 10, 5, 0.5)
    assert param.min_val == 1
    assert param.max_val == 10
    assert param.value == 5
    assert param.scale == 0.5

def test_save_data_init():
    """SaveDataが正しく初期化されることをテスト"""
    data = SaveData()
    assert data.url is None
    assert data.file_path is None
    assert data.seika_path == "C:/Program Files/510Product/AssistantSeika"
    assert data.voice is None
    assert data.chunk_size == 100
    assert data.interval == 0.5
    assert isinstance(data.effect, defaultdict)
    assert isinstance(data.emotion, defaultdict)
    assert data.effect.default_factory() == defaultdict(OptionParam)
    assert data.emotion.default_factory() == defaultdict(OptionParam)

def test_load_config(data_manager, test_config_file):
    """load_configが正しく設定をロードできることをテスト"""
    data_manager.load_config(test_config_file)
    assert data_manager.data.url == "http://example.com"
    assert data_manager.data.file_path == "test.txt"
    assert data_manager.data.seika_path == "C:/Seika"
    assert data_manager.data.voice == "voice1"
    assert data_manager.data.chunk_size == 200
    assert data_manager.data.interval == 1.0
    assert data_manager.data.effect["voice1"]["volume"].min_val == 0
    assert data_manager.data.effect["voice1"]["volume"].max_val == 100
    assert data_manager.data.effect["voice1"]["volume"].value == 50
    assert data_manager.data.effect["voice1"]["volume"].scale == 1
    assert data_manager.data.effect["voice1"]["speed"].min_val == 50
    assert data_manager.data.effect["voice1"]["speed"].max_val == 150
    assert data_manager.data.effect["voice1"]["speed"].value == 100
    assert data_manager.data.effect["voice1"]["speed"].scale == 5
    assert data_manager.data.emotion["voice1"]["happy"].min_val == 0
    assert data_manager.data.emotion["voice1"]["happy"].max_val == 100
    assert data_manager.data.emotion["voice1"]["happy"].value == 75
    assert data_manager.data.emotion["voice1"]["happy"].scale == 1

def test_load_config_file_not_found(data_manager):
    """load_configがファイルが存在しない場合でもエラーにならないことをテスト"""
    data_manager.load_config("nonexistent_config.json")
    assert data_manager.data.url is None
    assert data_manager.data.file_path is None
    assert data_manager.data.seika_path == "C:/Program Files/510Product/AssistantSeika"
    assert data_manager.data.voice is None
    assert data_manager.data.chunk_size == 100
    assert data_manager.data.interval == 0.5

# --- 2-1. dict2OptionParam テスト ---

def test_dict2OptionParam_full(data_manager):
    """全キー揃い → 正しく変換"""
    d = {"min_val": 0, "max_val": 100, "value": 50, "step": 2.0}
    param = data_manager.dict2OptionParam(d)
    assert param.min_val == 0
    assert param.max_val == 100
    assert param.value == 50
    assert param.scale == 2.0

def test_dict2OptionParam_missing_keys(data_manager):
    """一部キー欠損 → 該当フィールドNone"""
    d = {"min_val": 0, "value": 50}
    param = data_manager.dict2OptionParam(d)
    assert param.min_val == 0
    assert param.max_val is None
    assert param.value == 50
    assert param.scale is None

def test_dict2OptionParam_empty(data_manager):
    """空辞書 → 全フィールドNone"""
    param = data_manager.dict2OptionParam({})
    assert param.min_val is None
    assert param.max_val is None
    assert param.value is None
    assert param.scale is None

# --- 2-2. 異常系・後方互換性テスト ---

def test_load_config_invalid_json(data_manager, tmpdir):
    """不正JSON → JSONDecodeError"""
    config_file = tmpdir.join("invalid.json")
    config_file.write("not valid json {{{")
    with pytest.raises(json.JSONDecodeError):
        data_manager.load_config(str(config_file))

def test_load_config_partial(data_manager, tmpdir):
    """一部キーのみ → デフォルト値で補填"""
    config_data = {"url": "http://example.com"}
    config_file = tmpdir.join("partial.json")
    config_file.write(json.dumps(config_data))
    data_manager.load_config(str(config_file))
    assert data_manager.data.url == "http://example.com"
    assert data_manager.data.file_path is None
    assert data_manager.data.seika_path == "C:/Program Files/510Product/AssistantSeika"
    assert data_manager.data.voice is None
    assert data_manager.data.chunk_size == 100
    assert data_manager.data.interval == 0.5

def test_load_config_old_format(data_manager, tmpdir):
    """旧形式（volume_*, speed_*）→ 正しく変換"""
    config_data = {
        "voice": "voice1",
        "volume_min": 0, "volume_max": 100, "volume_val": 50, "volume_step": 1.0,
        "speed_min": 50, "speed_max": 200, "speed_val": 100, "speed_step": 5.0,
    }
    config_file = tmpdir.join("old_format.json")
    config_file.write(json.dumps(config_data))
    data_manager.load_config(str(config_file))
    assert data_manager.data.effect["voice1"]["volume"].min_val == 0
    assert data_manager.data.effect["voice1"]["volume"].max_val == 100
    assert data_manager.data.effect["voice1"]["volume"].value == 50
    assert data_manager.data.effect["voice1"]["volume"].scale == 1.0
    assert data_manager.data.effect["voice1"]["speed"].min_val == 50
    assert data_manager.data.effect["voice1"]["speed"].max_val == 200
    assert data_manager.data.effect["voice1"]["speed"].value == 100
    assert data_manager.data.effect["voice1"]["speed"].scale == 5.0

# --- 2-3. ラウンドトリップテスト ---

def test_save_load_roundtrip(data_manager, tmpdir):
    """保存→読込で全データ保持（scale/stepバグ検出）"""
    data_manager.data.url = "http://example.com/test"
    data_manager.data.voice = "voice1"
    data_manager.data.chunk_size = 150
    data_manager.data.interval = 1.5
    data_manager.data.effect["voice1"]["volume"].set_value(0, 100, 50, 2.0)
    data_manager.data.emotion["voice1"]["happy"].set_value(0, 100, 75, 5.0)

    config_file = str(tmpdir.join("roundtrip.json"))
    data_manager.save_config(config_file)

    dm2 = DataManager()
    dm2.load_config(config_file)

    assert dm2.data.url == "http://example.com/test"
    assert dm2.data.voice == "voice1"
    assert dm2.data.chunk_size == 150
    assert dm2.data.interval == 1.5
    assert dm2.data.effect["voice1"]["volume"].min_val == 0
    assert dm2.data.effect["voice1"]["volume"].max_val == 100
    assert dm2.data.effect["voice1"]["volume"].value == 50
    assert dm2.data.effect["voice1"]["volume"].scale == 2.0
    assert dm2.data.emotion["voice1"]["happy"].min_val == 0
    assert dm2.data.emotion["voice1"]["happy"].max_val == 100
    assert dm2.data.emotion["voice1"]["happy"].value == 75
    assert dm2.data.emotion["voice1"]["happy"].scale == 5.0

def test_save_config(data_manager, tmpdir):
    """save_configが正しく設定を保存できることをテスト"""
    # 設定を変更
    data_manager.data.url = "http://new_example.com"
    data_manager.data.chunk_size = 300
    # 保存先のファイルパス
    config_file = tmpdir.join("new_config.json")
    # 設定を保存
    data_manager.save_config(str(config_file))
    # ファイルの内容を読み込み
    with open(str(config_file), "r", encoding="utf-8") as f:
        saved_config = json.load(f)
    # 保存されたデータが正しいことを確認
    assert saved_config["url"] == "http://new_example.com"
    assert saved_config["chunk_size"] == 300