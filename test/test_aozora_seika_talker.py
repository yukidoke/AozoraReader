import pytest
from unittest.mock import patch, MagicMock
from src.aozora_seika_talker import AozoraSeikaTalker
from src.config import SaveData, OptionParam
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

    # --- 1-1. split_text_into_chunks エッジケース ---

    def test_split_empty_string(self, talker):
        """空文字列 → 空リスト"""
        chunks = talker.split_text_into_chunks("")
        assert chunks == []

    def test_split_single_short_paragraph(self, talker):
        """chunk_size未満の短い段落 → 1チャンク"""
        chunks = talker.split_text_into_chunks("短いテキスト", chunk_size=200)
        assert len(chunks) == 1
        assert chunks[0] == "短いテキスト"

    def test_split_long_paragraph_with_punctuation(self, talker):
        """chunk_size超の段落が句読点で分割される"""
        text = "これは長い段落です。句読点で分割されます。さらに続きます。"
        chunks = talker.split_text_into_chunks(text, chunk_size=20)
        assert len(chunks) == 2
        assert chunks[0] == "これは長い段落です。"
        assert chunks[1] == "句読点で分割されます。さらに続きます。"

    def test_split_long_paragraph_no_punctuation(self, talker):
        """句読点なしの長い段落 → 分割不能で1チャンク"""
        text = "あいうえおかきくけこさしすせそ"
        chunks = talker.split_text_into_chunks(text, chunk_size=10)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_exact_boundary(self, talker):
        """段落結合時の境界値テスト（len(current)+len(para)+2 == chunk_size）"""
        # 3 + 7 + 2 = 12 == chunk_size → 結合される
        text = "あああ\n\nいいいいいいい"
        chunks = talker.split_text_into_chunks(text, chunk_size=12)
        assert len(chunks) == 1
        assert chunks[0] == "あああ\n\nいいいいいいい"

    def test_split_multiple_short_paragraphs_merged(self, talker):
        """短い段落が結合されて1チャンクになる"""
        text = "あ。\n\nい。\n\nう。"
        chunks = talker.split_text_into_chunks(text, chunk_size=20)
        assert len(chunks) == 1
        assert chunks[0] == "あ。\n\nい。\n\nう。"

    # --- 1-2. get_aozora_text エッジケース ---

    @patch('src.aozora_seika_talker.requests.get')
    def test_get_aozora_text_no_main_text_div(self, mock_get, talker):
        """main_text div なし → (None, title, author)"""
        mock_response = MagicMock()
        mock_response.text = """
        <h1 class="title">作品タイトル</h1>
        <h2 class="author">作者名</h2>
        <div class="other">本文なし</div>
        """
        mock_get.return_value = mock_response
        text, title, author = talker.get_aozora_text("http://example.com")
        assert text is None
        assert title == "作品タイトル"
        assert author == "作者名"

    @patch('src.aozora_seika_talker.requests.get')
    def test_get_aozora_text_no_title_no_author(self, mock_get, talker):
        """タイトル・作者タグなし → デフォルト値"""
        mock_response = MagicMock()
        mock_response.text = """
        <div class="main_text">本文テキスト</div>
        """
        mock_get.return_value = mock_response
        text, title, author = talker.get_aozora_text("http://example.com")
        assert text is not None
        assert title == "タイトル不明"
        assert author == "作者不明"

    @patch('src.aozora_seika_talker.requests.get')
    def test_get_aozora_text_ruby_without_rb(self, mock_get, talker):
        """<rb>なしの<ruby> → ruby.textフォールバック"""
        mock_response = MagicMock()
        mock_response.text = """
        <h1 class="title">タイトル</h1>
        <h2 class="author">作者</h2>
        <div class="main_text"><ruby>漢字<rt>かんじ</rt></ruby></div>
        """
        mock_get.return_value = mock_response
        text, title, author = talker.get_aozora_text("http://example.com")
        assert text is not None
        assert "漢字" in text

    # --- 1-3. speak_text パラメータ付きテスト ---

    @patch('src.aozora_seika_talker.time.sleep')
    @patch('src.aozora_seika_talker.subprocess.run')
    def test_speak_text_with_effect(self, mock_run, mock_sleep, talker):
        """effectパラメータがコマンドに含まれること"""
        talker.data.voice = "結月ゆかり"
        talker.voice_dic = {"結月ゆかり": "1"}
        effect_param = OptionParam()
        effect_param.set_value(0, 100, 50, 10.0)
        talker.data.effect["結月ゆかり"]["speed"] = effect_param

        mock_run.return_value.returncode = 0
        result = talker.speak_text("テスト")
        assert result is True

        cmd = mock_run.call_args[0][0]
        assert "-speed" in cmd
        assert str(50 / 10.0) in cmd

    @patch('src.aozora_seika_talker.time.sleep')
    @patch('src.aozora_seika_talker.subprocess.run')
    def test_speak_text_with_emotion(self, mock_run, mock_sleep, talker):
        """emotionパラメータがコマンドに含まれること"""
        talker.data.voice = "結月ゆかり"
        talker.voice_dic = {"結月ゆかり": "1"}
        emotion_param = OptionParam()
        emotion_param.set_value(0, 100, 75, 10.0)
        talker.data.emotion["結月ゆかり"]["happiness"] = emotion_param

        mock_run.return_value.returncode = 0
        result = talker.speak_text("テスト")
        assert result is True

        cmd = mock_run.call_args[0][0]
        assert "-emotion" in cmd
        assert "happiness" in cmd
        assert str(75 / 10.0) in cmd

    # --- 1-4. get_voice_params 異常系 ---

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_get_voice_params_not_in_dic(self, mock_run, talker):
        """voice_dicにない音声名 → 早期リターン"""
        mock_run.return_value = MagicMock(stdout="  1 結月ゆかり\n")
        talker.get_voice_params("存在しない音声")
        # get_voice_listの1回のみ呼ばれ、paramsの取得は行われない
        assert mock_run.call_count == 1

    @patch('src.aozora_seika_talker.subprocess.run')
    def test_get_voice_params_subprocess_error(self, mock_run, talker):
        """subprocess失敗 → 例外なく終了"""
        mock_run.side_effect = [
            MagicMock(stdout="  1 結月ゆかり\n"),
            subprocess.CalledProcessError(1, ["cmd"])
        ]
        # 例外が発生しないことを確認
        talker.get_voice_params("結月ゆかり")

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