# 開発者向けドキュメント

## 開発環境のセットアップ

### uvを使用する場合（推奨）

```bash
# 依存関係をインストール（開発用依存関係を含む）
uv sync --dev

# テストを実行
uv run pytest

# カバレッジ付きでテストを実行
uv run pytest --cov=src --cov-report=html

# アプリケーションを起動
uv run aozora-reader
```

### pipを使用する場合

```bash
# 仮想環境を作成
python -m venv .venv

# 仮想環境を有効化（Windows）
.venv\Scripts\activate

# 仮想環境を有効化（macOS/Linux）
source .venv/bin/activate

# 開発モードでインストール
pip install -e ".[dev]"

# テストを実行
pytest

# アプリケーションを起動
aozora-reader
```

## プロジェクト構造

```
aozora-reader/
├── src/                      # ソースコード
│   ├── aozora_seika_talker.py  # メインロジック
│   ├── config.py              # 設定管理
│   ├── main.py                # GUIとエントリーポイント
│   └── reader_worker.py       # バックグラウンドスレッド
├── test/                     # テストコード
│   ├── test_aozora_seika_talker.py
│   ├── test_config.py
│   ├── test_main.py
│   └── test_reader_worker.py
├── pyproject.toml           # プロジェクト設定
├── uv.lock                  # 依存関係ロックファイル（uv用）
└── README.md                # ユーザー向けドキュメント
```

## テスト

### テストの実行

```bash
# すべてのテストを実行
uv run pytest

# 詳細表示
uv run pytest -vv

# カバレッジレポート生成
uv run pytest --cov=src --cov-report=html
# htmlcov/index.html をブラウザで開く
```

### テストカバレッジ

現在のテストカバレッジ: **55テスト** が全て成功

- ビジネスロジック層（aozora_seika_talker.py）: 22テスト
- データ層（config.py）: 13テスト
- スレッド層（reader_worker.py）: 8テスト
- GUI層（main.py）: 12テスト

## ビルド

### PyInstallerでスタンドアロンEXEを作成

```bash
# PyInstallerをインストール
uv add --dev pyinstaller

# EXEを作成
uv run pyinstaller main.spec

# 生成物はdist/フォルダに出力されます
```

## 依存関係の管理

### 新しいパッケージを追加

```bash
# 本番環境用の依存関係を追加
uv add package-name

# 開発用の依存関係を追加
uv add --dev package-name
```

### 依存関係の更新

```bash
# すべての依存関係を更新
uv lock --upgrade

# 特定のパッケージを更新
uv lock --upgrade-package package-name
```

## コードスタイル

- PEP 8に準拠
- 型ヒントは必須ではないが、推奨
- ドキュメント文字列は日本語で記述

## ライセンス

このプロジェクトはLGPL-3.0-or-laterライセンスで配布されています。
詳細は[LICENSE](./LICENSE)ファイルを参照してください。
