# AssistantSeika関連ドキュメント

VOICEROID2（64bit）, VOICEROID+EX, CeVIO（CS6.1/CS7）, CeVIO AI（8.1.5以降）, ガイノイドTalk, A.I.VOICE, VOICEVOX, COEIROINK, LMROID, SHAREVOX, ITVOICE, AivisSpeech Engine, SAPI等の音声合成製品を制御するプログラム(公式ページより)。

http機能を有効化することによりhttpで操作可能。現在はSeikaSay2.exeという付属ファイルを用いてCLI操作を行っているが、コマンド出力の整形が必要かつインストールされるファイルではなくダウンロード時に添付されるファイルであることから
扱いにくい。そこでhttp操作へ移行するため、知見をまとめる。

## 基本設定

`[ ] 音声保存時に再生デバイスをキャプチャする`

上記設定のチェックを外すことで、音声保存時に音声を再生させないことが可能となる。

## HTTP

AS上で`HTTP機能を利用する`にチェックボックスを入れ、`起動する`ボタンを押下することで起動。

設定可能項目
- 待ち受けアドレス
- ポート
- BASIC認証 ユーザID
- BASIC認証 パスワード

### URL

```bash
curl -X GET http://SeikaServerUser:SeikaServerPassword@localhost:7180 # GET
curl -X POST -H "Content-Type: application/json" -d "{}" http://SeikaServerUser:SeikaServerPassword@localhost:7180 # POST
```

## パラメータ

### /VERSION
`GET`

ASのバージョン文字列
```json
{
    "version":"20250113\/a"
}
```

### /AVATOR2

`GET`

利用可能な話者一覧
```json
[
    {"cid":60011,"isalias":false,"name":"琴葉 茜","platform":"64","prod":"AIVOICEAPI"},
    {"cid":60021,"isalias":false,"name":"琴葉 葵","platform":"64","prod":"AIVOICEAPI"},
    {"cid":60041,"isalias":false,"name":"結月 ゆかり","platform":"64","prod":"AIVOICEAPI"},
    {"cid":60051,"isalias":false,"name":"紲星 あかり","platform":"64","prod":"AIVOICEAPI"},
    {"cid":68000,"isalias":false,"name":"鳴花ヒメ","platform":"64","prod":"AIVOICEAPI"},
    {"cid":68001,"isalias":false,"name":"鳴花ミコト","platform":"64","prod":"AIVOICEAPI"}
]
```

#### /AVATOR2/{cid}
`GET`

話者のデフォルトパラメタ
```json
{
    "effect":{
        "volume":{"value":1,"min":0.0,"max":2.0,"step":0.01},
        "speed":{"value":1,"min":0.10,"max":5.0,"step":0.01},
        "pitch":{"value":1,"min":0.10,"max":5.0,"step":0.01},
        "intonation":{"value":1,"min":0.0,"max":5.0,"step":0.01},
        "shortpause":{"value":150,"min":80.0,"max":500.0,"step":1.00},
        "longpause":{"value":370,"min":80.0,"max":2000.0,"step":1.00}
    },
    "emotion":{
        "喜び":{"value":0,"min":0.00,"max":1.00,"step":0.01},
        "怒り":{"value":0,"min":0.00,"max":1.00,"step":0.01},
        "悲しみ":{"value":0,"min":0.00,"max":1.00,"step":0.01}
    }
}
```

##### /AVATOR2/{cid}/current
`GET`

話者の現在のパラメタ
```json
{
    "effect":{
        "volume":{"value":1,"min":0.0,"max":2.0,"step":0.01},
        "speed":{"value":1,"min":0.10,"max":5.0,"step":0.01},
        "pitch":{"value":1,"min":0.10,"max":5.0,"step":0.01},
        "intonation":{"value":1,"min":0.0,"max":5.0,"step":0.01},
        "shortpause":{"value":150,"min":80.0,"max":500.0,"step":1.00},
        "longpause":{"value":370,"min":80.0,"max":2000.0,"step":1.00}
    },
    "emotion":{
        "喜び":{"value":0,"min":0.00,"max":1.00,"step":0.01},
        "怒り":{"value":0,"min":0.00,"max":1.00,"step":0.01},
        "悲しみ":{"value":0,"min":0.00,"max":1.00,"step":0.01}
    }
}
```

### /PLAY2/{cid}
`POST`

話者に発声させる。`talktext`以外は省略可能。
```json
{
  "talktext":"おはようございますー！",
  "effects":{
    "speed"     :1.0,
    "volume"    :1.0,
    "pitch"     :1.0,
    "intonation":1.0
  },
  "emotions":{
    "怒り"   :0.00,
    "喜び"   :1.00,
    "悲しみ" :0.20
  }
}
```

返却値
```json
{"message" : "tts cid 60011 called." }
```

### /PLAYASYNC2/{cid}
`POST`

`/PLAY2/{cid}`の非同期版。発声終了を待たない。


### /SAVE2/{cid}
`POST`

音声データを得る。
音声キャプチャ設定によって発声されるかが変わる。

#### /SAVE2/{cid}/{sampleRate}
`POST`

音声データのサンプリングレートを指定して取得する。
