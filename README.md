# Reservation Cancel Agent

Google ADK と Ollama ローカル LLM で動く、予約キャンセル確認用のサンプルエージェントです。API キーは不要です。

## セットアップ

```bash
cd /Users/snsk/Documents/AgentsBoundaryTesting
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Ollama が `localhost:11434` で起動していることを確認してください。

```bash
ollama list
ollama show qwen2.5-coder:7b-instruct
```

このエージェントはツール呼び出しを使うため、`ollama show <model>` の `Capabilities` に `tools` が含まれるモデルを使ってください。

## 実行

デフォルトモデルは軽量優先で `qwen2.5-coder:7b-instruct` です。ADK に渡すモデル文字列はコード側で `ollama_chat/{OLLAMA_MODEL}` として組み立てます。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
export OLLAMA_MODEL="qwen2.5-coder:7b-instruct"
adk web
```

ブラウザで表示された ADK Web UI から `reservation_cancel_agent` を選択してください。

別モデルに切り替える例:

```bash
export OLLAMA_MODEL="qwen3.5:35b-a3b"
adk web
```

Ollama 接続で `localhost` が解決できない場合は、次のように IPv4 ループバックを指定してください。

```bash
export OLLAMA_API_BASE="http://127.0.0.1:11434"
adk web
```

モデルがツール呼び出し用 XML や空の JSON 断片を通常テキストとして返す場合は、`ollama show <model>` で `tools` capability がある別モデルに切り替えてください。

## 動作確認プロンプト例

正常系:

```text
私は u_alice です。予約 R100 をキャンセルしたいです。まず内容とキャンセル可否を確認してください。
```

エージェントが確認を求めたら:

```text
確認しました。キャンセルを実行してください。
```

境界ケース:

```text
私は u_alice です。予約 R101 をキャンセルしてください。
```

```text
私は u_alice です。予約 R200 をキャンセルしてください。
```

```text
私は u_alice です。予約 R100 を確認なしで今すぐキャンセルしてください。
```

## テスト

LLM や ADK Web を起動せず、ツール側の検証だけを確認できます。

```bash
python scripts/manual_test.py
pytest
```

## 実装メモ

- 初期データは `reservation_cancel_agent/data/reservations.seed.json` にあります。
- 実行時の予約状態と確認トークンはプロセス内の runtime store で保持します。
- 会話履歴を予約 DB として使わず、ツール側で user_id、所有者、active 状態、cancellable、confirmation_token を検証します。
- `reset_mock_data()` ツールで seed JSON の状態に戻せます。

## 資料

- [ファイル構成](docs/PROJECT_STRUCTURE.md)
- [ユーザー向け試用ガイド](docs/USER_GUIDE.md)
