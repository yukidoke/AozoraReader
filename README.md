# AozoraReader

**AozoraReader**は青空文庫からテキストを取得し、合成音声に朗読してもらうためのスクリプトです。

<!-- # DEMO 気が向いたら追加します -->

# Requirement

* AssistantSeika 20250113/a

<details>
<summary> Pythonスクリプトを実行する場合 </summary>

* Python 3.10.6
* requests 2.32.3
* beautifulsoup4 4.13.3
* PySide6 6.8.2.1

動作を確認したバージョンです。他のバージョンでも動くかもしれません。
</details>

# Installation

[AssistantSeika公式サイト](https://wiki.hgotoh.jp/documents/tools/assistantseika/assistantseika-000)を確認して、AssistantSeikaを使用できるようにしてください。

Releaseからzipファイルをダウンロードして解凍してください。

<details>
<summary> Pythonスクリプトを実行する場合 </summary>

1. このレポジトリをダウンロードしてください。

2. [Pythonをインストール](https://www.python.org)してください。

3. 以下のコマンドを実行して必要なライブラリをインストールしてください。
```bash
python -m pip install requests beautifulSoup4 PyQt5
```

4. 以下のコマンドを実行してスクリプト本体を実行してください。
```bash
python main.py
```
</details>

# Usage

以下の動画を参照してください。
気が向けばドキュメントも追加します。

https://www.nicovideo.jp/watch/sm44725477

# License

**AozoraReader** is licensed under the GNU Lesser General Public License v3.0 (LGPLv3).  
You can redistribute it and/or modify it under the terms of the License.  
See the [LICENSE](./LICENSE) file for the full text of the license.

### v1.1.1以前について

v1.1.0以前には、GUIライブラリとしてPyQt5を使用していました。
しかし、PyQt5はGPLv3ライセンスであるためMITライセンスでAozoraReaderを配布することはライセンス違反でした。
そこで、LGPLライセンスであるPySide6を使用するコードへと変更し、v1.1.1以前のReleaseを削除しました。
