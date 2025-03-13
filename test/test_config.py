import pytest
import json
import os
from src.config import DataManager, SaveData, OptionParam
from collections import defaultdict

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