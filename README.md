# Big Brother
![RASPBIAN](https://img.shields.io/badge/RASPBIAN%20JESSIE-March%202016-green.svg) ![Python](https://img.shields.io/badge/Python-2.7-blue.svg)

誰かがトイレに入った時や出た時に slack に通知する bot

## デバイス
* Raspberry Pi Type B

### 距離センサー
* HC-SR04
* GP2Y0A710K
  * MCP3208 (ADコンバーター)

## 設定ファイル
1. toire.cfg.org をコピーして toire.cfg を作る
2. `hook_url` と `channel` を設定する
3. 使用する距離センサーを sensor で決める
