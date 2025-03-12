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

import time
from PySide6.QtCore import QThread, Signal

# 読み上げ処理を行うワーカースレッド
class ReaderWorker(QThread):
    progress_updated = Signal(int, int)
    current_text_updated = Signal(str)
    reading_finished = Signal()
    reading_error = Signal(str)
    
    def __init__(self, talker, text_chunks, parent=None):
        super().__init__(parent)
        self.talker = talker
        self.chunks = text_chunks
        self.current_chunk = 0

    def run(self):
        self.talker.is_reading = True
        chunk_count = len(self.chunks)
        
        while self.current_chunk < chunk_count and self.talker.is_reading:
            # 一時停止中は待機
            while self.talker.pause_reading and self.talker.is_reading:
                time.sleep(0.1)
                
            if not self.talker.is_reading:
                break
                
            chunk = self.chunks[self.current_chunk]
            self.current_text_updated.emit(chunk)
            
            success = self.talker.speak_text(chunk)
            if not success:
                self.reading_error.emit("音声の読み上げに失敗しました。AssistantSeikaの設定を確認してください。")
                break
                
            self.current_chunk += 1
            self.progress_updated.emit(self.current_chunk, chunk_count)
            
        self.talker.is_reading = False
        self.reading_finished.emit()
        
    def get_current_position(self):
        return self.current_chunk

# テキストの取得を行うワーカースレッド
class FetchWorker(QThread):
    fetch_completed = Signal(str, str, str)
    fetch_error = Signal(str)
    
    def __init__(self, talker, url, parent=None):
        super().__init__(parent)
        self.talker = talker
        self.url = url
        
    def run(self):
        text, title, author = self.talker.get_aozora_text(self.url)
        if text:
            self.fetch_completed.emit(text, title, author)
        else:
            self.fetch_error.emit(f"テキストの取得に失敗しました: {author}")