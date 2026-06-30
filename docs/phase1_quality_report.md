# Phase 1 Quality Report

## 判定

Phase 1は完了。

合格理由:

- 1つの質問に対して、No Memory / Raw Memory / ERINYS + Qwen の差が画面上で読める。
- No Memoryは賢いが、記憶がないためexact planを作れない。
- Raw Memoryは通常のRAG失敗として、古い記憶・矛盾・合成IDを混ぜてしまう。
- ERINYS + Qwenは危険文脈を落とし、現在有効な介護準備だけをQwenへ渡す。
- Qwen Cloud live接続で動作している。
- persistent memoryを保存し、再実行後のERINYS + Qwen回答で使える。
- トークン削減率が60%を超えている。

## 実装した改善

### Seed強化

合成メモリseedを10件から31件へ増やした。

内訳:

- selected: 9
- contradiction: 5
- blocked: 5
- demoted: 5
- ignored: 7

追加した種類:

- 現在有効な通院準備
- 明日の正確なcheck-in時刻、taxi pickup時刻、accessible drop-off
- 古い移動ルート
- 古い食事予定
- 古い身体状態の前提
- 合成の保険ID、住所、ポータル番号、ドアコード、電話番号
- 関係ない長期記憶ノイズ

### Memory Governance

`decision_note`を追加し、各判断の理由をUIへ出せるようにした。

ERINYSは以下を行う:

- private identifierをblockedにする
- 新しい記憶と矛盾する古い記憶をcontradictionにする
- 古いが危険度の低い記憶をdemotedにする
- 低優先度の記憶をignoredにする
- Qwenへ渡すcontextはselectedだけにする

### Persistent Memory Proof

`POST /memories`を追加し、ユーザーが保存したメモリを`runtime_memory.json`へ永続化できるようにした。

保存後の挙動:

- `/health`にpersisted memory countが出る
- `/memories`でseed memoryとuser memoryを監査できる
- `/run/governance`で保存済み`u001`がselectedになる
- `/run/benchmark`でERINYS + Qwenだけが保存済みメモリを使う

### Raw Memory Baseline

Raw Memoryは通常のmemory-augmented assistant baselineとして、全メモリをQwenへ渡す。

このbaselineはわざと馬鹿にしない。取得した記憶をすべて有用そうな文脈として扱うため、古い9:00/8:10 train/east stairway系の記憶、合成住所やSYNTH系ID、関係ない長期記憶まで混ざる。これにより「LLMが弱い」のではなく「memory governanceがないRAGが危ない」ことを見せる。

### UI改善

改善後の画面:

- 上部バナーにトークン削減率を表示
- No Memoryにexact timing/transportを知れないことを表示
- Raw Memoryにconfident but conflicted、private ID leak、stale routeを表示
- ERINYS + Qwenにexact current plan、private ID block、memory decision説明を表示
- Memory Decisionsにselected / conflicts / demoted / blockedの数を表示
- conflictsとblockedを先に見せ、審査員が危険回避を先に読めるようにした
- デスクトップとモバイル幅で横方向の大きな破綻が出ないよう調整

## Live Quality Evidence

Qwen Cloud live status:

```json
{"mode":"live","model":"qwen3.7-plus","api_key_configured":true}
```

Live benchmark result:

```text
No Memory tokens: 77
Raw Memory tokens: 783
ERINYS + Qwen tokens: 278
Savings: 64%
No Memory exact plan: not possible without memory
Raw answer contains synthetic identifier: true
Raw answer contains stale route conflict: true
ERINYS answer contains 13:35 taxi / 14:20 check-in: true
ERINYS answer contains synthetic identifier: false
```

Decision counts:

```text
selected: 9
selected after persistent memory save: 10
contradiction: 5
blocked: 5
demoted: 5
ignored: 7
```

Screenshots:

- `docs/design/phase1-live-quality-final.png`
- `docs/design/phase1-live-quality-mobile-final5.png`

## Verification

Passed:

```text
.venv/bin/python -m pytest  # 13 passed
.venv/bin/ruff check src tests
.venv/bin/python -m compileall src
npm run build
Qwen Cloud live benchmark
Chrome headless desktop screenshot
Chrome headless mobile screenshot
```

## Remaining Non-Phase1 Work

These are not Phase1 blockers:

- Alibaba Cloud deployment proof
- public repository packaging
- final README judging map
- architecture diagram
- 3-minute video script and recording
