import pytest
from PySide6.QtWidgets import QApplication, QFileDialog
from src import main

@pytest.fixture(scope="module")
def app():
    """PySide6アプリケーションのfixture"""
    app = QApplication([])
    yield app
    app.quit()

def test_aozorareadergui_init(app):
    """AozoraReaderGUIの初期化をテスト"""
    window = main.AozoraReaderGUI()
    assert window.windowTitle() == 'AozoraReader'
    assert window.centralWidget() is not None
    assert window.url_input is not None
    assert window.file_path is not None
    assert window.voice_combo is not None
    assert window.chunk_size is not None
    assert window.start_button is not None
    assert window.pause_button is not None
    assert window.stop_button is not None

def test_fetch_text(app, monkeypatch):
    """fetch_textメソッドのテスト"""
    window = main.AozoraReaderGUI()
    url = "http://example.com/aozora.txt"
    window.url_input.setText(url)

    # FetchWorkerのstartメソッドが呼ばれることを確認
    class MockFetchWorker:
        def __init__(self, talker, url):
            self.url = url
        def start(self):
            pass
    
    monkeypatch.setattr(main, "FetchWorker", MockFetchWorker)
    
    window.fetch_text()
    assert window.fetch_button.text() == "取得中..."
    assert window.fetch_worker.url == url

def test_select_file(app, monkeypatch):
    """select_fileメソッドのテスト"""
    window = main.AozoraReaderGUI()
    file_path = "test.txt"
    file_content = "テストファイルの内容"

    # QFileDialog.getOpenFileNameのモック
    def mock_get_open_file_name(*args, **kwargs):
        return file_path, ""
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_open_file_name)

    # open関数のモック
    def mock_open(path, mode, encoding):
        assert path == file_path
        assert mode == 'r'
        assert encoding == 'utf-8'
        class MockFile:
            def read(self):
                return file_content
        return MockFile()
    monkeypatch.setattr("builtins.open", mock_open)

    # process_textが呼ばれることを確認
    def mock_process_text(text, title, author):
        assert text == file_content
        assert title == "test.txt"
        assert author == "ローカルファイル"
    monkeypatch.setattr(window, "process_text", mock_process_text)

    window.select_file()
    assert window.file_path.text() == file_path

def test_process_text(app, monkeypatch):
    """process_textメソッドのテスト"""
    window = main.AozoraReaderGUI()
    text = "テストテキスト"
    title = "テストタイトル"
    author = "テスト作者"

    window.process_text(text, title, author)
    assert window.text_display.toPlainText() == text
    assert window.title_label.text() == f"タイトル: {title}"
    assert window.author_label.text() == f"作者: {author}"
    assert len(window.text_chunks) > 0
    assert window.start_button.isEnabled() == True

def test_start_reading(app, monkeypatch):
    """start_readingメソッドのテスト"""
    window = main.AozoraReaderGUI()
    text = "テストテキスト"
    title = "テストタイトル"
    author = "テスト作者"
    window.process_text(text, title, author)

    # ReaderWorkerのstartメソッドが呼ばれることを確認
    class MockReaderWorker:
        def __init__(self, talker, text_chunks):
            pass
        def start(self):
            pass
    monkeypatch.setattr(main, "ReaderWorker", MockReaderWorker)

    window.start_reading()
    assert window.start_button.isEnabled() == False
    assert window.pause_button.isEnabled() == True
    assert window.stop_button.isEnabled() == True

def test_toggle_pause(app, monkeypatch):
    """toggle_pauseメソッドのテスト"""
    window = main.AozoraReaderGUI()
    text = "テストテキスト"
    title = "テストタイトル"
    author = "テスト作者"
    window.process_text(text, title, author)
    
    class MockReaderWorker:
        def __init__(self, talker, text_chunks):
            self.talker = talker
        def start(self):
            pass
    monkeypatch.setattr(main, "ReaderWorker", MockReaderWorker)
    window.start_reading()

    window.toggle_pause()
    assert window.talker.pause_reading == True
    assert window.pause_button.text() == "再開"

    window.toggle_pause()
    assert window.talker.pause_reading == False
    assert window.pause_button.text() == "一時停止"

def test_stop_reading(app, monkeypatch):
    """stop_readingメソッドのテスト"""
    window = main.AozoraReaderGUI()
    text = "テストテキスト"
    title = "テストタイトル"
    author = "テスト作者"
    window.process_text(text, title, author)
    
    class MockReaderWorker:
        def __init__(self, talker, text_chunks):
            self.talker = talker
        def start(self):
            pass
        def terminate(self):
            pass
        def wait(self):
            pass
    monkeypatch.setattr(main, "ReaderWorker", MockReaderWorker)
    window.start_reading()

    window.stop_reading()
    assert window.talker.is_reading == False
    assert window.talker.pause_reading == False
    assert window.start_button.isEnabled() == True
    assert window.pause_button.isEnabled() == False
    assert window.stop_button.isEnabled() == False

def test_save_load_config(app, monkeypatch):
    """save_configとload_configメソッドのテスト"""
    window = main.AozoraReaderGUI()
    config_file = "test_config.json"
    monkeypatch.setattr(window, "save_filename", config_file)

    # save_configのテスト
    class MockDataManager:
        def __init__(self):
            self.data = main.DataManager().data
        def save_config(self, filename):
            assert filename == config_file
        def load_config(self, filename):
            self.data.url = "test_url"
            self.data.file_path = "test_file"
            self.data.seika_path = "test_seika"
            self.data.chunk_size = 100
            self.data.interval = 1.0
            self.data.voice = "test_voice"
    monkeypatch.setattr(main, "DataManager", MockDataManager)
    window.save_config()

    # load_configのテスト
    window.load_config()
    assert window.url_input.text() == "test_url"
    assert window.file_path.text() == "test_file"
    assert window.seika_path.text() == "test_seika"
    assert window.chunk_size.value() == 100
    assert window.chunk_interval.value() == 1.0
    assert window.voice_combo.currentText() == "test_voice"