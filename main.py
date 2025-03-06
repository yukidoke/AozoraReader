"""
MIT License

Copyright (c) 2025 yukidoke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.
"""

import json
import sys
import os
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QComboBox, QPushButton, QTextEdit, QSpinBox, 
                            QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, 
                            QProgressBar, QFileDialog, QMessageBox,
                            QSlider, QDoubleSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class AozoraSeikaTalker:
    def __init__(self, seika_path="C:/Program Files/510Product/AssistantSeika"):
        """
        AssistantSeikaを使用して青空文庫の作品を音声読み上げするクラス
        
        Parameters:
        -----------
        seika_path : str
            AssistantSeikaのインストールパス
        """
        self.seika_path = seika_path
        self.seika_console = os.path.join(seika_path, "SeikaSay2.exe")
        self.is_reading = False
        self.pause_reading = False
        self.voice_dic = {}
        self.talk_speed = 1.0
        self.talk_volume = 1.0
        self.chunk_interval = 0.5
        
    def get_aozora_text(self, url):
        """
        青空文庫のURLから本文テキストを抽出する
        
        Parameters:
        -----------
        url : str
            青空文庫の作品URL
            
        Returns:
        --------
        str : 抽出された本文
        """
        try:
            response = requests.get(url)
            response.encoding = 'shift_jis'  # 青空文庫はShift-JISエンコーディング
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 作品タイトルの取得
            title = soup.find('h1', class_='title')
            author = soup.find('h2', class_='author')
            title_text = title.text if title else "タイトル不明"
            author_text = author.text if author else "作者不明"
            
            # 本文の抽出（青空文庫の本文はclassが'main_text'のdiv内にある）
            main_text_div = soup.find('div', class_='main_text')
            if not main_text_div:
                return None, title_text, author_text
                
            # ルビや注釈などの不要なタグを処理
            for ruby in main_text_div.find_all('ruby'):
                ruby_text = ruby.find('rb')
                if ruby_text:
                    ruby.replace_with(ruby_text.text)
                else:
                    ruby.replace_with(ruby.text)
            
            for rp in main_text_div.find_all('rp'):
                rp.decompose()
                
            for rt in main_text_div.find_all('rt'):
                rt.decompose()
            
            # テキストを取得し、整形
            text = main_text_div.get_text()
            
            # 不要な空白行を削除
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text, title_text, author_text
            
        except Exception as e:
            return None, "エラー", str(e)
        
    def set_speed(self, speed):
        self.talk_speed = speed

    def set_volume(self, volume):
        self.talk_volume = volume

    def set_interval(self, interval):
        self.chunk_interval = interval
    
    def split_text_into_chunks(self, text, chunk_size=200):
        """
        テキストを適切な大きさのチャンクに分割する
        
        Parameters:
        -----------
        text : str
            分割するテキスト
        chunk_size : int
            チャンクのサイズ（文字数）
            
        Returns:
        --------
        list : テキストチャンクのリスト
        """
        # 段落ごとに分割
        paragraphs = text.split('\n\n')
        chunks = []
        
        current_chunk = ""
        for paragraph in paragraphs:
            # 長い段落は文で分割
            if len(paragraph) > chunk_size:
                sentences = re.split(r'(。|、|！|？|,|\.)', paragraph)
                i = 0
                while i < len(sentences):
                    if i+1 < len(sentences) and sentences[i+1] in ['。', '、', '！', '？', ',', '.']:
                        sentence = sentences[i] + sentences[i+1]
                        i += 2
                    else:
                        sentence = sentences[i]
                        i += 1
                    
                    if len(current_chunk) + len(sentence) <= chunk_size:
                        current_chunk += sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence
            else:
                if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def speak_text(self, text, voice_name="結月ゆかり"):
        """
        テキストをAssistantSeikaで読み上げる
        
        Parameters:
        -----------
        text : str
            読み上げるテキスト
        voice_name : str
            使用する音声の名前
        pause_duration : float
            読み上げ間の一時停止の秒数
        """

        cmd = [
            self.seika_console,
            "-cid", self.voice_dic[voice_name],  # チャンネルID
            "-speed", str(self.talk_speed),
            "-volume", str(self.talk_volume),
            "-t", text.replace('\n', ' ')  # 改行をスペースに置換
        ]

        try:
            subprocess.run(cmd, check=True)
            time.sleep(self.chunk_interval)  # 読み上げ間の間隔
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_voice_list(self):
        """
        AssistantSeikaで利用可能な音声リストを取得
        
        Returns:
        --------
        list : 利用可能な音声の名前リスト
        """
        cmd = [
            self.seika_console,
            "-list"
        ]

        # talker = re.compile(r'\s*(\d+)\s+(.+?)\s+-\s+(.+)\s*')
        talker = re.compile(r'\s*(\d+)\s+(.+?)\s*')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            voices = []
            self.voice_dic = {}
            for line in result.stdout.splitlines():
                print(line)
                m = talker.fullmatch(line)
                if not m == None:
                    voice_name = m.group(2)
                    voices.append(voice_name)
                    self.voice_dic[m.group(2)] = m.group(1)
            return voices
        except:
            # エラーが発生した場合、デフォルトの声リストを返す
            return ["結月ゆかり", "琴葉茜", "琴葉葵", "東北きりたん", "京町セイカ"]

    def get_voice_speed(self, voice_name):
        if voice_name in self.voice_dic:
            cmd = [
                self.seika_console,
                "-cid", self.voice_dic[voice_name],
                "-params"
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    m = re.fullmatch(r'effect\s*:\s*speed\s*=\s*(.+)\s*\[(.+?)～(.+?),\s*step\s*(.+?)\]\s*', line)
                    if not m == None:
                        return float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
            except:
                return None, None, None, None
        return None, None, None, None
    
    def get_voice_volume(self, voice_name):
        if voice_name in self.voice_dic:
            cmd = [
                self.seika_console,
                "-cid", self.voice_dic[voice_name],
                "-params"
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    m = re.fullmatch(r'effect\s*:\s*volume\s*=\s*(.+)\s*\[(.+?)～(.+?),\s*step\s*(.+?)\]\s*', line)
                    if not m == None:
                        return float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
            except:
                return None, None, None, None
        return None, None, None, None

# 読み上げ処理を行うワーカースレッド
class ReaderWorker(QThread):
    progress_updated = pyqtSignal(int, int)
    current_text_updated = pyqtSignal(str)
    reading_finished = pyqtSignal()
    reading_error = pyqtSignal(str)
    
    def __init__(self, talker, text_chunks, voice_name, parent=None):
        super().__init__(parent)
        self.talker = talker
        self.chunks = text_chunks
        self.voice_name = voice_name
        self.current_chunk = 0

    def set_voice(self, voice_name):
        self.voice_name = voice_name

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
            
            success = self.talker.speak_text(chunk, self.voice_name)
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
    fetch_completed = pyqtSignal(str, str, str)
    fetch_error = pyqtSignal(str)
    
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
        self.talk_speed = QSlider()
        self.talk_speed.setOrientation(1)
        self.speed_step = 1
        self.talk_speed.setRange(1, 1)
        self.talk_speed.setValue(1)
        self.talk_speed.valueChanged.connect(self.on_update_speed)
        params_layout.addWidget(self.speed_label)
        params_layout.addWidget(self.talk_speed)

        # 音量設定
        self.volume_label = QLabel('音量:')
        self.volume = QSlider()
        self.volume.setOrientation(1)
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
        
    @pyqtSlot(str, str, str)
    def on_fetch_completed(self, text, title, author):
        self.process_text(text, title, author)
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("テキスト取得")
        
    @pyqtSlot(str)
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

    @pyqtSlot(str)
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
    sys.exit(app.exec_())