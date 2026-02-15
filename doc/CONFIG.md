# CONFIG.md

configファイルの形式

## v1.0.0
```json
{
    "url": "https://www.aozora.gr.jp/cards/000879/files/127_15260.html",
    "file_path": "D:/sandbox/AozoraReader/クソデカ羅生門.txt",
    "seika_path": "D:\\sandbox\\AozoraReader\\assistantseika20250113a\\SeikaSay2",
    "voice": "すずきつづみ  - CeVIOAI(64)",
    "chunk_size": 100,
    "speed_step": 1.0,
    "speed_min": 0,
    "speed_max": 100,
    "speed_val": 60,
    "volume_step": 1.0,
    "volume_min": 0,
    "volume_max": 100,
    "volume_val": 50
}
```

## v2.0.0
```json
{
    "url": "https://www.aozora.gr.jp/cards/000081/files/456_15050.html",
    "file_path": null,
    "seika_path": "D:\\sandbox\\AozoraReader\\assistantseika20250113a\\SeikaSay2",
    "voice": "すずきつづみ  - CeVIOAI(64)",
    "chunk_size": 100,
    "interval": 0.0,
    "effect": {
        "": {},
        "結月ゆかり": {},
        "すずきつづみ  - CeVIOAI(64)": {
            "volume": {
                "min_val": 0,
                "max_val": 100,
                "value": 50,
                "scale": 1.0
            },
            "speed": {
                "min_val": 0,
                "max_val": 100,
                "value": 65,
                "scale": 1.0
            },
            "pitch": {
                "min_val": 0,
                "max_val": 100,
                "value": 50,
                "scale": 1.0
            },
            "alpha": {
                "min_val": 0,
                "max_val": 100,
                "value": 50,
                "scale": 1.0
            },
            "intonation": {
                "min_val": 0,
                "max_val": 100,
                "value": 50,
                "scale": 1.0
            }
        }
    },
    "emotion": {
        "": {},
        "結月ゆかり": {},
        "すずきつづみ  - CeVIOAI(64)": {
            "クール": {
                "min_val": 0,
                "max_val": 100,
                "value": 50,
                "scale": 1.0
            },
            "照れ": {
                "min_val": 0,
                "max_val": 100,
                "value": 0,
                "scale": 1.0
            },
            "怒り": {
                "min_val": 0,
                "max_val": 100,
                "value": 0,
                "scale": 1.0
            },
            "喜び": {
                "min_val": 0,
                "max_val": 100,
                "value": 30,
                "scale": 1.0
            },
            "ひそひそ": {
                "min_val": 0,
                "max_val": 100,
                "value": 0,
                "scale": 1.0
            }
        }
    }
}
```

## v2.1.0
```json
{
    "config_version": "v2.1.0",
    "url": "https://www.aozora.gr.jp/cards/000081/files/456_15050.html",
    "file_path": null,
    "main_voice": "すずきつづみ  - CeVIOAI(64)",
    "sub_voice": "さとうささら  - CeVIOAI(64)",
    "chunk_size": 100,
    "interval": 0.0,
    "parametors": {
        "琴葉 茜": {
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
    },
    "http_settings": {
        "address": "localhost",
        "port": 7180,
        "basic_userid": "SeikaServerUser",
        "basec_password": "SeikaServerPassword"
    }
}
```