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

import requests
from bs4 import BeautifulSoup
import os
import re
import subprocess
import time
from config import SaveData

class AozoraSeikaTalker:
    def __init__(self, save_data : SaveData, seika_path="C:/Program Files/510Product/AssistantSeika"):
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
        self.data : SaveData = save_data
        
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
    
    def speak_text(self, text : str):
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

        cmd : list = [
            self.seika_console,
            "-cid", self.voice_dic[self.data.voice]
        ]

        if self.data.effect[self.data.voice] != None:
            for key in self.data.effect[self.data.voice]:
                cmd.append(f'-{key}')
                cmd.append(str(self.data.effect[self.data.voice][key].value / self.data.effect[self.data.voice][key].scale))

        if self.data.emotion[self.data.voice] != None:
            for key in self.data.emotion[self.data.voice]:
                cmd.append(f'-emotion')
                cmd.append(key)
                cmd.append(str(self.data.emotion[self.data.voice][key].value / self.data.emotion[self.data.voice][key].scale))

        cmd.append('-t')
        cmd.append(text.replace('\n', ' '))

        try:
            print(cmd)
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

    def get_voice_params(self, voice_name : str):
        """
        現在の音声で利用可能なパラメータを取得
        """
        self.get_voice_list()
        if not voice_name in self.voice_dic: return

        cmd = [
            self.seika_console,
            "-cid", self.voice_dic[voice_name],
            "-params"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                effect = re.fullmatch(r'effect\s*:\s*(.+?)\s*=\s*(.+)\s*\[(.+?)～(.+?),\s*step\s*(.+?)\]\s*', line)
                emotion = re.fullmatch(r'emotion\s*:\s*(.+?)\s*=\s*(.+)\s*\[(.+?)～(.+?),\s*step\s*(.+?)\]\s*', line)

                if effect != None:
                    print(effect.group(1))
                    def_val = float(effect.group(2))
                    min_val = float(effect.group(3))
                    max_val = float(effect.group(4))
                    stp_val = float(effect.group(5))

                    stp_val = 1 / stp_val
                    def_val = int(def_val * stp_val)
                    min_val = int(min_val * stp_val)
                    max_val = int(max_val * stp_val)

                    if self.data.effect[voice_name][effect.group(1)].value != None:
                            def_val = self.data.effect[voice_name][effect.group(1)].value
                            def_val = min(def_val, max_val)
                            def_val = max(def_val, min_val)

                    self.data.effect[voice_name][effect.group(1)].set_value(min_val, max_val, def_val, stp_val)

                if emotion != None:
                    print(emotion.group(1))
                    def_val = float(emotion.group(2))
                    min_val = float(emotion.group(3))
                    max_val = float(emotion.group(4))
                    stp_val = float(emotion.group(5))

                    stp_val = 1 / stp_val
                    def_val = int(def_val * stp_val)
                    min_val = int(min_val * stp_val)
                    max_val = int(max_val * stp_val)

                    if self.data.emotion[voice_name][emotion.group(1)].value != None:
                        def_val = self.data.emotion[voice_name][emotion.group(1)].value
                        def_val = min(def_val, max_val)
                        def_val = max(def_val, min_val)
                    self.data.emotion[voice_name][emotion.group(1)].set_value(min_val, max_val, def_val, stp_val)

        except Exception as e:
            print(e)
            return