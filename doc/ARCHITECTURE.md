# 設計

本システムの設計をまとめます。
nowセクションに現在の設計・futureセクションに目標となる設計を記述します。

## now

### AozoraReaderGUI

システムのエントリーポイントとなるクラス。

役割
- GUIの表示
- GUIへのデータ表示
- GUIからのデータ受け取り・更新

### AozoraSeikaTalker

役割
- 青空文庫からのデータ取得
- 本文のチャンク分割
- ASへの読み上げ依頼
- ASとの互換レイヤ

### DataManager

役割
- configのセーブ/ロード

### SaveData

役割
- configとして保存されるデータの定義

### OptionParam

役割
- 感情/エフェクトパラメータの定義

### ReaderWorker

役割
- AozoraSeikaTalkerの操作
- AozoraReaderGUIへの状態変更通知

### FetchWorker

役割
- text fetch関連のイベント通知

## future

若干汚いMVCかな

### View

GUIの表示・データ更新を行う
データをユーザに表示し、ユーザの入力をデータに変更するレイヤ

### Config

Modelの役割
configのセーブ/ロードを行う。
古いバージョンのconfigからの変換も担当。
ロードボタン時にロードし、終了時にセーブ、それ以外はファイルに触らない
config.jsonをデータへと変換する

### ASM

Modelの役割
ASとの抽象レイヤ

### DataFectch

Modelの役割
青空文庫・テキストファイルとの抽象レイヤ

### Controller

ビジネスロジック
- テキストデータの解釈
- チャンク分割
- 読み上げ依頼
