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

import json
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QComboBox, QPushButton, QTextEdit, QSpinBox, 
                            QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, 
                            QProgressBar, QFileDialog, QMessageBox,
                            QSlider, QDoubleSpinBox)
from PySide6.QtCore import Slot, Qt

from aozora_seika_talker import AozoraSeikaTalker
from reader_worker import ReaderWorker, FetchWorker

class AozoraReaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.talker = AozoraSeikaTalker()
        self.reader_worker = None
        self.text_chunks = []
        self.full_text = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('青空文庫音声読み上げアプリ')
        self.setGeometry(100, 100, 800, 600)
        
        # メインウィジェットとレイアウト
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 入力セクション
        input_group = QGroupBox('入力設定')
        input_layout = QVBoxLayout()
        
        # URL入力
        url_layout = QHBoxLayout()
        url_label = QLabel('青空文庫URL:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://www.aozora.gr.jp/cards/...')
        self.fetch_button = QPushButton('テキスト取得')
        self.fetch_button.clicked.connect(self.fetch_text)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_button)
        
        # テキストファイル読み込み
        file_layout = QHBoxLayout()
        file_label = QLabel('または、テキストファイル:')
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText('テキストファイルを選択...')
        self.file_button = QPushButton('参照...')
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.file_button)
        
        # 音声設定
        voice_layout = QHBoxLayout()
        voice_label = QLabel('話者:')
        self.voice_combo = QComboBox()
        self.voice_combo.currentTextChanged.connect(self.on_voice_changed)
        self.voice_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        
        # AssistantSeikaのパスを設定
        seika_layout = QHBoxLayout()
        seika_label = QLabel('AssistantSeikaのパス:')
        self.seika_path = QLineEdit('C:/Program Files/510Product/AssistantSeika')
        self.seika_path.textChanged.connect(self.update_seika_path)
        self.refresh_button = QPushButton('音声一覧更新')
        self.refresh_button.clicked.connect(self.update_voice_list)
        seika_layout.addWidget(seika_label)
        seika_layout.addWidget(self.seika_path)
        seika_layout.addWidget(self.refresh_button)
        
        # 初期音声リストの取得
        self.update_voice_list()
        
        chunk_label = QLabel('チャンクサイズ:')
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(50, 1000)
        self.chunk_size.setValue(200)
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addWidget(chunk_label)
        voice_layout.addWidget(self.chunk_size)

        # 設定の保存・読み込み
        save_layout = QHBoxLayout()
        self.save_filename = os.path.join(os.path.dirname(sys.argv[0]),'config.json')
        self.config_save = QPushButton('設定を保存')
        self.config_save.clicked.connect(self.save_config)
        save_layout.addWidget(self.config_save)
        self.config_load = QPushButton('設定を読み込み')
        self.config_load.clicked.connect(self.load_config)
        save_layout.addWidget(self.config_load)

        # 速度設定
        params_layout = QHBoxLayout()
        self.speed_label = QLabel('話速:')
        self.talk_speed = QSlider(Qt.Horizontal)
        self.speed_step = 1
        self.talk_speed.setRange(1, 1)
        self.talk_speed.setValue(1)
        self.talk_speed.valueChanged.connect(self.on_update_speed)
        params_layout.addWidget(self.speed_label)
        params_layout.addWidget(self.talk_speed)

        # 音量設定
        self.volume_label = QLabel('音量:')
        self.volume = QSlider(Qt.Horizontal)
        self.volume_step = 1
        self.volume.setRange(1, 1)
        self.volume.setValue(1)
        self.volume.valueChanged.connect(self.on_update_volume)
        params_layout.addWidget(self.volume_label)
        params_layout.addWidget(self.volume)

        # チャンク間隔
        chunk_label = QLabel('チャンク間隔:')
        self.chunk_interval = QDoubleSpinBox()
        self.chunk_interval.setRange(0.0, 10.0)
        self.chunk_interval.setDecimals(2)
        self.chunk_interval.setSingleStep(0.01)
        self.chunk_interval.setValue(0.5)
        self.chunk_interval.setSuffix('秒')
        self.chunk_interval.valueChanged.connect(self.on_update_interval)
        params_layout.addWidget(chunk_label)
        params_layout.addWidget(self.chunk_interval)
        
        input_layout.addLayout(url_layout)
        input_layout.addLayout(file_layout)
        input_layout.addLayout(seika_layout)
        input_layout.addLayout(voice_layout)
        input_layout.addLayout(params_layout)
        input_layout.addLayout(save_layout)
        input_group.setLayout(input_layout)

        # テキスト表示セクション
        text_group = QGroupBox('テキスト内容')
        text_layout = QVBoxLayout()
        
        self.title_label = QLabel('タイトル: ')
        self.author_label = QLabel('作者: ')
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.author_label)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        text_layout.addWidget(self.text_display)
        
        text_group.setLayout(text_layout)
        
        # 進捗表示セクション
        progress_group = QGroupBox('読み上げ状態')
        progress_layout = QVBoxLayout()
        
        self.current_text = QTextEdit()
        self.current_text.setReadOnly(True)
        self.current_text.setMaximumHeight(150)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        control_layout = QHBoxLayout()
        self.start_button = QPushButton('読み上げ開始')
        self.start_button.clicked.connect(self.start_reading)
        self.start_button.setEnabled(False)
        
        self.pause_button = QPushButton('一時停止')
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        
        self.stop_button = QPushButton('停止')
        self.stop_button.clicked.connect(self.stop_reading)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        
        progress_layout.addWidget(self.current_text)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(control_layout)
        
        progress_group.setLayout(progress_layout)
        
        # レイアウトの追加
        main_layout.addWidget(input_group)
        main_layout.addWidget(text_group)
        main_layout.addWidget(progress_group)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def update_seika_path(self):
        self.talker.seika_path = self.seika_path.text()
        self.talker.seika_console = os.path.join(self.talker.seika_path, "SeikaSay2.exe")
        
    def update_voice_list(self):
        current_voice = self.voice_combo.currentText()
        
        self.voice_combo.clear()
        voices = self.talker.get_voice_list()
        self.voice_combo.addItems(voices)
        
        # 前に選択されていた音声を再選択
        if current_voice in voices:
            index = voices.index(current_voice)
            self.voice_combo.setCurrentIndex(index)
            
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "テキストファイルを選択", "", "テキストファイル (*.txt)")
        if file_path:
            self.file_path.setText(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # ファイル名からタイトルを取得
                title = os.path.basename(file_path)
                
                self.process_text(text, title, "ローカルファイル")
                
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"ファイルの読み込みに失敗しました: {e}")
            
    def fetch_text(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "警告", "URLを入力してください")
            return
            
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("取得中...")
        
        # テキスト取得をワーカースレッドで実行
        self.fetch_worker = FetchWorker(self.talker, url)
        self.fetch_worker.fetch_completed.connect(self.on_fetch_completed)
        self.fetch_worker.fetch_error.connect(self.on_fetch_error)
        self.fetch_worker.start()

    def save_config(self):
        data = {
            "url": self.url_input.text(),
            "file_path": self.file_path.text(),
            "seika_path": self.seika_path.text(),
            "voice": self.voice_combo.currentText(),
            "chunk_size": self.chunk_size.value(),
            "speed_step": self.speed_step,
            "speed_min": self.talk_speed.minimum(),
            "speed_max": self.talk_speed.maximum(),
            "speed_val": self.talk_speed.value(),
            "volume_step": self.volume_step,
            "volume_min": self.volume.minimum(),
            "volume_max": self.volume.maximum(),
            "volume_val": self.volume.value(),
            "interval": self.chunk_interval.value()
        }
        with open(self.save_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_config(self):
        try:
            with open(self.save_filename, "r", encoding="utf-8") as f:
                conf = json.load(f)
                self.url_input.setText(conf['url'])
                self.file_path.setText(conf['file_path'])
                self.seika_path.setText(conf['seika_path'])
                self.chunk_size.setValue(conf['chunk_size'])

                self.update_voice_list()
                if conf['voice'] in self.talker.voice_dic:
                    self.voice_combo.setCurrentText(conf['voice'])
                    self.speed_step = conf['speed_step']
                    self.talk_speed.setRange(conf['speed_min'], conf['speed_max'])
                    self.talk_speed.setValue(conf['speed_val'])
                    self.volume_step = conf['volume_step']
                    self.volume.setRange(conf['volume_min'], conf['volume_max'])
                    self.volume.setValue(conf['volume_val'])

                if 'interval' in conf:
                    self.chunk_interval.setValue(conf['interval'])
        except:
            QMessageBox.warning(self, "警告", "設定ファイルの読み込みに失敗しました")
        
    @Slot(str, str, str)
    def on_fetch_completed(self, text, title, author):
        self.process_text(text, title, author)
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("テキスト取得")
        
    @Slot(str)
    def on_fetch_error(self, error_message):
        QMessageBox.critical(self, "エラー", error_message)
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("テキスト取得")
        
    def process_text(self, text, title, author):
        self.full_text = text
        self.text_display.setText(text)
        self.title_label.setText(f"タイトル: {title}")
        self.author_label.setText(f"作者: {author}")
        
        # テキストをチャンクに分割
        chunk_size = self.chunk_size.value()
        self.text_chunks = self.talker.split_text_into_chunks(text, chunk_size)
        
        # 読み上げボタンを有効化
        self.start_button.setEnabled(True)
        
    def start_reading(self):
        if not self.text_chunks:
            QMessageBox.warning(self, "警告", "読み上げるテキストがありません。テキストを取得してください。")
            return
            
        voice_name = self.voice_combo.currentText()
        
        # 既存のワーカーが存在し、実行中の場合は停止
        if self.reader_worker and self.reader_worker.isRunning():
            self.reader_worker.terminate()
            self.reader_worker.wait()

        # チャンク設定を適用
        text = self.full_text
        chunk_size = self.chunk_size.value()
        self.text_chunks = self.talker.split_text_into_chunks(text, chunk_size)

        # 新しいワーカーを作成して開始
        self.reader_worker = ReaderWorker(self.talker, self.text_chunks, voice_name)
        self.reader_worker.progress_updated.connect(self.update_progress)
        self.reader_worker.current_text_updated.connect(self.update_current_text)
        self.reader_worker.reading_finished.connect(self.on_reading_finished)
        self.reader_worker.reading_error.connect(self.on_reading_error)
        
        self.reader_worker.start()
        
        # ボタンの状態を更新
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.talker.pause_reading = False
        self.pause_button.setText("一時停止")
        
    def update_progress(self, current, total):
        progress = int(current * 100 / total)
        self.progress_bar.setValue(progress)
        
    def update_current_text(self, text):
        self.current_text.setText(text)
        
    def toggle_pause(self):
        if not self.talker.is_reading:
            return
            
        self.talker.pause_reading = not self.talker.pause_reading
        
        if self.talker.pause_reading:
            self.pause_button.setText("再開")
        else:
            self.pause_button.setText("一時停止")
        
    def stop_reading(self):
        if self.talker.is_reading:
            self.talker.is_reading = False
            self.talker.pause_reading = False
            
            if self.reader_worker:
                self.reader_worker.terminate()
                self.reader_worker.wait()
                
            self.on_reading_finished()
            
    def on_reading_finished(self):
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("一時停止")
        
    def on_reading_error(self, error_message):
        QMessageBox.critical(self, "エラー", error_message)
        self.on_reading_finished()

    @Slot(str)
    def on_voice_changed(self, text):
        if not self.reader_worker == None:
            self.reader_worker.set_voice(text)
        if not self.talker == None:
            dflt, vmin, vmax, step = self.talker.get_voice_speed(text)
            if not dflt == None:
                scale = 1 / step
                self.speed_step = scale
                self.talk_speed.setRange(int(vmin * scale), int(vmax * scale))
                self.talk_speed.setValue(int(dflt * scale))
                self.talker.set_speed(dflt)
            dflt, vmin, vmax, step = self.talker.get_voice_volume(text)
            if not dflt == None:
                scale = 1 / step
                self.volume_step = scale
                self.volume.setRange(int(vmin * scale), int(vmax * scale))
                self.volume.setValue(int(dflt * scale))
                self.talker.set_volume(dflt)

    def on_update_speed(self):
        if not self.talker == None:
            value = float(self.talk_speed.value()) / self.speed_step
            self.talker.set_speed(value)
            self.speed_label.setText(f"話速: {value:.2f}")

    def on_update_volume(self):
        if not self.talker == None:
            value = float(self.volume.value()) / self.volume_step
            self.talker.set_volume(value)
            self.volume_label.setText(f"音量: {value:.2f}")

    def on_update_interval(self):
        if not self.talker == None:
            self.talker.set_interval(self.chunk_interval.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AozoraReaderGUI()
    window.show()
    sys.exit(app.exec())