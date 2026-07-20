# Project Structure

このプロジェクトは、Google ADK の Python エージェントを Ollama ローカル LLM で動かす予約キャンセル検証用サンプルです。

```text
.
├── README.md
├── pyproject.toml
├── reservation_cancel_agent/
│   ├── __init__.py
│   ├── action_bridge.py
│   ├── agent.py
│   ├── settings.py
│   ├── store.py
│   ├── tools.py
│   └── data/
│       └── reservations.seed.json
├── scripts/
│   └── manual_test.py
├── tests/
│   └── test_tools.py
└── docs/
    ├── PROJECT_STRUCTURE.md
    └── USER_GUIDE.md
```

## 主要ファイル

- `reservation_cancel_agent/agent.py`: ADK が読み込む `root_agent` を定義します。モデルは `LiteLlm(model=get_litellm_model())` で設定し、環境変数から切り替えられます。
- `reservation_cancel_agent/action_bridge.py`: ローカルモデルが `{"action": ..., "arguments": ...}` のような ReAct 風 JSON を通常テキストとして返した場合に、許可済みツールだけ ADK function call へ変換します。
- `reservation_cancel_agent/settings.py`: `OLLAMA_MODEL` と `OLLAMA_API_BASE` のデフォルト値と、`ollama_chat/{model_name}` の組み立てを管理します。
- `reservation_cancel_agent/store.py`: seed JSON から初期化されるプロセス内 runtime store です。予約状態と確認トークンはここに保持されます。
- `reservation_cancel_agent/tools.py`: ADK に渡すツール関数です。ユーザー、所有者、状態、キャンセル可否、確認トークンの検証は store 側で実行します。
- `reservation_cancel_agent/data/reservations.seed.json`: モック予約 DB の初期データです。
- `scripts/manual_test.py`: LLM を使わずにツール層の正常系と境界ケースを確認する手動テストです。
- `tests/test_tools.py`: pytest 用の最小テストです。

## 安全境界

LLM の会話履歴は予約 DB として使いません。キャンセル実行時は、ツール側で必ず次を検証します。

- `user_id` が存在すること
- `reservation_id` がそのユーザーの所有物であること
- 予約の `status` が `active` であること
- 予約の `cancellable` が `true` であること
- `prepare_cancellation()` で発行された `confirmation_token` が対象ユーザーと予約に一致すること
- ADK 補助ツール `confirm_and_cancel_reservation()` でも、明示確認フラグを受けた後に内部で `prepare_cancellation()` と `cancel_reservation()` を順に実行すること
- ReAct 風 JSON の補正は `ALLOWED_ACTIONS` に含まれるツール名だけを変換し、未知の action は実行しないこと

このため、LLM が誤って「キャンセルしてよい」と判断しても、ツール検証に失敗する操作は拒否されます。
