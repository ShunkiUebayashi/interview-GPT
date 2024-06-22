# interview-GPT

このプロジェクトは、ユーザがAIを使用して就職活動の面接練習を行うためのブラウザアプリケーションです。
ユーザはテーマを設定し、GPT-3.5 Turbo、GPT-4、またはGPT-4oモデルを使用して対話を行うことができます。
このアプリケーションは自身の研究を活用し、対話の逸脱を判定します。
これに加えて、対話の終了時にに面接の総評を示します。

## 機能

- 初期設定画面
  - OpenAI APIキーの設定
  - モデル選択（GPT-3.5 Turbo、GPT-4、GPT-4o）
  - テーマの設定

- メインシステム画面
  - チャット形式での面接練習
  - リセットボタン : チャット履歴をリセット
  - テーマの変更ボタン : 対話のテーマを変更
  - モデルの変更(e.g.GPT-3.5 -> GPT-4o)
  - 対話の評価ボタン : 対話の評価結果を表示

## セットアップ
### レポジトリのclone
```bash
git clone https://github.com/ShunkiUebayashi/interview-GPT.git
cd interview-GPT
```
### 必要なライブラリのインストール

以下のコマンドを実行して必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```
### アプリの起動
以下のコマンドでアプリが起動します。
```bash
python app.py
```
アプリの起動後、http://127.0.0.1:5000/ にアクセスすることでアプリを使用できます。
## ToDo
- [ ] 音声認識への対応
- [ ] 読み上げシステムの統合
## 参考文献
- https://www.ipsj.or.jp/event/taikai/86/WEB/data/pdf/4R-01.html

