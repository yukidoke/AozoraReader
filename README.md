# AozoraReader

**AozoraReader**は青空文庫からテキストを取得し、合成音声に朗読してもらうためのスクリプトです。

<!-- # DEMO 気が向いたら追加します -->

# Requirement

* AssistantSeika 20250113/a

<details>
<summary> Pythonスクリプトを実行する場合 </summary>

* Python 3.10 以上
* requests 2.32.3 以上
* beautifulsoup4 4.13.3 以上
* PySide6 6.8.0 以上

</details>

# Installation

[AssistantSeika公式サイト](https://wiki.hgotoh.jp/documents/tools/assistantseika/assistantseika-000)を確認して、AssistantSeikaを使用できるようにしてください。

Releaseからzipファイルをダウンロードして解凍してください。

<details>
<summary> Pythonスクリプトを実行する場合 </summary>

## 前提条件

- [Python 3.10以上](https://www.python.org)をインストールしてください
- （推奨）[uv](https://docs.astral.sh/uv/)をインストールしてください

## uvを使用する場合（推奨）

1. このリポジトリをクローンまたはダウンロードしてください
```bash
git clone https://github.com/yourusername/aozora-reader.git
cd aozora-reader
```

2. 依存パッケージをインストールして実行してください
```bash
# 依存関係をインストール
uv sync

# アプリケーションを起動
uv run aozora-reader
```

3. テストを実行する場合
```bash
# 開発用依存関係を含めてインストール
uv sync --dev

# テストを実行
uv run pytest
```

## pipを使用する場合

1. このリポジトリをクローンまたはダウンロードしてください

2. 仮想環境を作成して有効化してください
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. 依存パッケージをインストールしてください
```bash
pip install -e .

# 開発用（テスト実行する場合）
pip install -e ".[dev]"
```

4. アプリケーションを起動してください
```bash
aozora-reader

# または
python -m src.main
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
