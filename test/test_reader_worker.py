import pytest
from src.reader_worker import ReaderWorker, FetchWorker
from PySide6.QtCore import Signal
from unittest.mock import MagicMock, patch

@pytest.fixture
def reader_worker():
    talker_mock = MagicMock()
    talker_mock.speak_text.return_value = True
    talker_mock.pause_reading = False
    text_chunks = ["chunk1", "chunk2"]
    return ReaderWorker(talker_mock, text_chunks)

@pytest.fixture
def fetch_worker():
    talker_mock = MagicMock()
    return FetchWorker(talker_mock, "http://example.com")

def test_reader_worker_initialization(reader_worker):
    """
    テストの意図: ReaderWorkerクラスが正しく初期化されることを確認する。
    仕様: ReaderWorkerのインスタンスが作成され、エラーが発生しないこと。
    """
    assert reader_worker is not None

def test_reader_worker_run(reader_worker):
    """
    テストの意図: ReaderWorkerのrunメソッドが正しく動作することを確認する。
    仕様:
        1. talker.speak_textが各chunkに対して呼び出されること。
        2. progress_updatedシグナルが適切な回数、適切な引数でemitされること。
        3. current_text_updatedシグナルが各chunkに対してemitされること。
        4. reading_finishedシグナルがemitされること。
    """
    progress_updated_mock = MagicMock()
    current_text_updated_mock = MagicMock()
    reading_finished_mock = MagicMock()
    reader_worker.progress_updated.connect(progress_updated_mock)
    reader_worker.current_text_updated.connect(current_text_updated_mock)
    reader_worker.reading_finished.connect(reading_finished_mock)
    
    reader_worker.run()
    
    assert reader_worker.talker.speak_text.call_count == 2
    assert progress_updated_mock.call_count == 2
    assert progress_updated_mock.call_args_list == [((1, 2),), ((2, 2),)]
    assert current_text_updated_mock.call_count == 2
    assert current_text_updated_mock.call_args_list == [(("chunk1",),), (("chunk2",),)]
    assert reading_finished_mock.call_count == 1

def test_reader_worker_get_current_position(reader_worker):
    """
    テストの意図: get_current_positionメソッドが現在の読み上げ位置を正しく返すことを確認する。
    仕様: runメソッド実行前は0を返し、runメソッド実行中は現在のchunk番号を返すこと。
    """
    assert reader_worker.get_current_position() == 0
    reader_worker.current_chunk = 1
    assert reader_worker.get_current_position() == 1

def test_reader_worker_speak_failure():
    """speak_textがFalse → reading_errorシグナル発行、中断"""
    talker_mock = MagicMock()
    talker_mock.speak_text.return_value = False
    talker_mock.pause_reading = False
    worker = ReaderWorker(talker_mock, ["chunk1", "chunk2"])

    reading_error_mock = MagicMock()
    reading_finished_mock = MagicMock()
    worker.reading_error.connect(reading_error_mock)
    worker.reading_finished.connect(reading_finished_mock)

    worker.run()

    assert talker_mock.speak_text.call_count == 1
    reading_error_mock.assert_called_once()
    reading_finished_mock.assert_called_once()

def test_reader_worker_stop_mid_reading():
    """is_readingが途中でFalse → ループ中断"""
    talker_mock = MagicMock()
    talker_mock.pause_reading = False
    def speak_side_effect(text):
        talker_mock.is_reading = False
        return True
    talker_mock.speak_text.side_effect = speak_side_effect

    worker = ReaderWorker(talker_mock, ["chunk1", "chunk2", "chunk3"])

    reading_finished_mock = MagicMock()
    worker.reading_finished.connect(reading_finished_mock)

    worker.run()

    assert talker_mock.speak_text.call_count == 1
    reading_finished_mock.assert_called_once()

def test_reader_worker_empty_chunks():
    """空チャンクリスト → 即座にreading_finished"""
    talker_mock = MagicMock()
    talker_mock.pause_reading = False
    worker = ReaderWorker(talker_mock, [])

    reading_finished_mock = MagicMock()
    worker.reading_finished.connect(reading_finished_mock)

    worker.run()

    talker_mock.speak_text.assert_not_called()
    reading_finished_mock.assert_called_once()

def test_fetch_worker_run_success(fetch_worker):
    """
    テストの意図: FetchWorkerのrunメソッドが成功した場合の動作を確認する。
    仕様:
        1. get_aozora_textが正しく呼び出されること。
        2. fetch_completedシグナルが適切な引数でemitされること。
    """
    fetch_worker.talker.get_aozora_text.return_value = ("text", "title", "author")
    fetch_completed_mock = MagicMock()
    fetch_worker.fetch_completed.connect(fetch_completed_mock)

    fetch_worker.run()

    fetch_worker.talker.get_aozora_text.assert_called_once_with(fetch_worker.url)
    fetch_completed_mock.assert_called_once_with("text", "title", "author")

def test_fetch_worker_run_failure(fetch_worker):
    """
    テストの意図: FetchWorkerのrunメソッドが失敗した場合の動作を確認する。
    仕様:
        1. get_aozora_textが正しく呼び出されること。
        2. fetch_errorシグナルが適切な引数でemitされること。
    """
    fetch_worker.talker.get_aozora_text.return_value = (None, "title", "error")
    fetch_error_mock = MagicMock()
    fetch_worker.fetch_error.connect(fetch_error_mock)

    fetch_worker.run()

    fetch_worker.talker.get_aozora_text.assert_called_once_with(fetch_worker.url)
    fetch_error_mock.assert_called_once_with("テキストの取得に失敗しました: error")