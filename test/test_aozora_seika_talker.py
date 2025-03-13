import pytest
from unittest.mock import patch, MagicMock
from src.aozora_seika_talker import AozoraSeikaTalker
from src.config import SaveData
import subprocess

@pytest.fixture
def save_data():
    return SaveData()

@pytest.fixture
def talker(save_data):
    return AozoraSeikaTalker(save_data, seika_path="dummy_seika_path")

class TestAozoraSeikaTalker:

    def test_init(self, talker):
        """
        テストの意図: AozoraSeikaTalkerの初期化が正しく行われることを確認する。
        仕様:
            - seika_pathが正しく設定されていること。
            - seika_consoleが正しく設定されていること。
            - is_reading, pause_readingが初期値で設定されていること。
            - voice_dicが初期化されていること。
            - talk_speed, talk_volume, chunk_intervalが初期値で設定されていること。
            - dataがSaveDataのインスタンスであること。
        """
        assert talker.seika_path == "dummy_seika_path"
        assert talker.seika_console == "dummy_seika_path\\SeikaSay2.exe"
        assert talker.is_reading == False
        assert talker.pause_reading == False
        assert talker.voice_dic == {}
        assert talker.talk_speed == 1.0
        assert talker.talk_volume == 1.0
        assert talker.chunk_interval == 0.5
        assert isinstance(talker.data, SaveData)

    @patch('src.aozora_seika_talker.requests.get')
    def test_get_aozora_text_success(self, mock_get, talker):
        """
        テストの意図: get_aozora_textが正常にテキストを取得できることを確認する。
        仕様:
            - requests.getが呼ばれること。
            - レスポンスのエンコーディングが'shift_jis'に設定されること。
            - BeautifulSoupが正しく使われること。
            - タイトルと本文が正しく抽出されること。
            - 不要なタグが適切に処理されること。
        """
        mock_response = MagicMock()
        mock_response.text = """
        <h1 class="title">作品タイトル</h1>
        <h2 class="author">作者名</h2>
        <div class="main_text">
            本文<ruby><rb>ルビ</rb><rt>ルビテキスト</rt></ruby><rp>（</rp><rt>注釈</rt><rp>）</rp>
        </div>
        """
        mock_get.return_value = mock_response
        text, title, author = talker.get_aozora_text("http://example.com")
        assert mock_get.called
        assert mock_response.encoding == 'shift_jis'
        assert title == "作品タイトル"
        assert author == "作者名"
        assert "本文ルビ" in text # ルビが正しく処理されているか確認
        assert "注釈" not in text # 注釈が削除されているか確認

    @patch('src.aozora_seika_talker.requests.get')
    def test_get_aozora_text_failure(self, mock_get, talker):
        """
        テストの意図: get_aozora_textがエラー発生時に適切な値を返すことを確認する。
        仕様:
            - requests.getが例外を発生させた場合、None, "エラー", エラーメッセージを返すこと。
        """
        mock_get.side_effect = Exception("Network error")
        text, title, author = talker.get_aozora_text("http://example.com")
        assert text is None
        assert title == "エラー"
        assert "Network error" in author

    def test_split_text_into_chunks(self, talker):
        """
        テストの意図: split_text_into_chunksがテキストを正しくチャンクに分割できることを確認する。
        仕様:
            - 指定されたchunk_sizeに基づいてテキストが分割されること。
            - 長い段落が文単位で分割されること。
        """
        text = "これは最初の段落です。\n\nこれは2番目の段落です。長文なので分割されます。これは2番目の段落の続きです。"
        chunks = talker.split_text_into_chunks(text, chunk_size=30)
        assert len(chunks) == 2
        assert chunks[0] == "これは最初の段落です。これは2番目の段落です。"
        assert chunks[1] == "長文なので分割されます。これは2番目の段落の続きです。"

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_speak_text_success(self, mock_run, talker):
        """
        テストの意図: speak_textが正常にAssistantSeikaを呼び出せることを確認する。
        仕様:
            - subprocess.runが正しく呼び出されること。
            - コマンドが正しく構成されていること。
            - 成功した場合にTrueを返すこと。
        """
        talker.data.voice = "結月ゆかり"
        talker.voice_dic = {"結月ゆかり": "1"}
        mock_run.return_value.returncode = 0
        result = talker.speak_text("テストテキスト")
        assert result == True
        cmd = [
            talker.seika_console,
            "-cid", "1",
            '-t', "テストテキスト"
        ]
        mock_run.assert_called_once_with(cmd, check=True)

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_speak_text_failure(self, mock_run, talker):
        """
        テストの意図: speak_textが失敗した場合にFalseを返すことを確認する。
        仕様:
            - subprocess.runがCalledProcessErrorを発生させた場合にFalseを返すこと。
        """
        talker.data.voice = "結月ゆかり"
        talker.voice_dic = {"結月ゆかり": "1"}
        mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])
        result = talker.speak_text("テストテキスト")
        assert result == False

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_get_voice_list_success(self, mock_run, talker):
        """
        テストの意図: get_voice_listが音声リストを正しく取得できることを確認する。
        仕様:
            - subprocess.runが正しく呼び出されること。
            - 音声リストが正しくパースされること。
            - voice_dicが正しく更新されること。
        """
        mock_run.return_value.stdout = "  1 結月ゆかり - VOICE1\n  2 琴葉茜 - VOICE2"
        voices = talker.get_voice_list()
        assert voices == ["結月ゆかり - VOICE1", "琴葉茜 - VOICE2"]
        assert talker.voice_dic == {"結月ゆかり - VOICE1": "1", "琴葉茜 - VOICE2": "2"}

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_get_voice_list_failure(self, mock_run, talker):
        """
        テストの意図: get_voice_listがエラー発生時にデフォルトの音声リストを返すことを確認する。
        仕様:
            - subprocess.runが例外を発生させた場合、デフォルトの音声リストを返すこと。
        """
        mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])
        voices = talker.get_voice_list()
        assert voices == ["結月ゆかり", "琴葉茜", "琴葉葵", "東北きりたん", "京町セイカ"]

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_get_voice_params_success(self, mock_run, talker, save_data):
        """
        テストの意図: get_voice_paramsが音声パラメータを正しく取得できることを確認する。
        仕様:
            - subprocess.runが正しく呼び出されること。
            - パラメータが正しくパースされ、SaveDataに設定されること。
        """
        talker.data.voice = "結月ゆかり - VOICE1"
        talker.voice_dic = {"結月ゆかり - VOICE1": "1"}
        mock_run.side_effect = [
            MagicMock(stdout="  1 結月ゆかり - VOICE1\n  2 琴葉茜 - VOICE2"),
            MagicMock(stdout="effect : speed = 1.0 [0.5～2.0, step 0.1]\nemotion : happiness = 0.0 [-1.0～1.0, step 0.1]")
        ]
        talker.get_voice_params("結月ゆかり - VOICE1")
        assert talker.data.effect["結月ゆかり - VOICE1"]["speed"].value == 10
        assert talker.data.emotion["結月ゆかり - VOICE1"]["happiness"].value == 0