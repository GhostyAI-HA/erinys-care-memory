# 開発プラン概要

## 決定事項

提出は Track 1: MemoryAgent に一本化する。

プロジェクト名:

```text
ERINYS Care Memory Decision Bench
```

一言で言うと:

```text
Qwenの回答は、記憶をただ全部入れるのではなく、ERINYSが選別・抑制・説明してから渡すことで安全で役に立つものになる。
```

これは医療アプリではない。介護・通院準備を題材にした、記憶ガバナンスのデモである。医療っぽい文脈を使う理由は、古い記憶、個人識別情報、矛盾、コンテキスト制限の問題が審査員に一瞬で伝わるから。

## 外部要件

参照元:

- Devpost hackathon page: https://qwencloud-hackathon.devpost.com/
- Qwen Cloud challenge page: https://www.qwencloud.com/challenge/hackathon

把握している要件:

- 締切: 2026-07-09 14:00 PDT。日本時間では 2026-07-10 06:00 JST。
- 対象トラック: Track 1 MemoryAgent。
- 必須技術: Qwen Cloudで使えるQwenモデルを使う。
- 提出物:
  - ライセンス付きの公開OSSリポジトリ
  - Alibaba Cloud上でバックエンドが動く証明
  - アーキテクチャ図
  - 公開デモ動画。目安は約3分
  - 機能説明テキスト
  - 選択トラック
- 評価比重:
  - Technical Depth & Engineering: 30%
  - Innovation & AI Creativity: 30%
  - Problem Value & Impact: 25%
  - Presentation & Documentation: 15%

## 勝つデモ

審査員に見せるのは、1つの質問に対する3種類の回答。

1. No Memory: 賢いが、記憶がないので正確な時刻・移動・制約は言えない。
2. Raw Memory: 記憶を全部入れる。古い予定、矛盾、合成の個人識別情報まで自然に混ざる。
3. ERINYS + Qwen: ERINYSが記憶を選別し、古い記憶を落とし、矛盾を見つけ、危ない記憶をブロックしてからQwenが正確な当日計画を答える。

見せたい瞬間:

```text
記憶を管理したから、Qwenの答えが変わった。
```

最初の20秒でこれが見えないと負ける。READMEを読まなくても、画面だけで差が伝わる状態にする。

## 現在地

完了済み:

- Qwen Cloudアカウントは有効。
- Qwen Cloud API keyはローカル `.env` に保存済み。
- Live Qwen呼び出しで `OK.` が返った。
- バックエンドの `/health` は Qwen `mode: live` を返す。
- 現在のLiveモデルは `qwen3.7-plus`。
- Reactの比較UIは存在する。
- Answer Diff BenchのDesign QAは通過済み。
- バックエンドは No Memory / Raw Memory / ERINYS + Qwen を比較できる。
- 合成の介護メモリseedは存在する。

まだ弱いところ:

- トークン削減率が、審査員に刺さるほど大きくない。
- Alibaba Cloudデプロイ証明が未完了。
- 公開リポジトリ、ライセンス、提出パッケージが未完了。
- 3分動画の台本と録画が未完了。

## 開発フェーズ

### フェーズ1: デモの差を一撃で見えるようにする

ゴール:

```text
最初の画面だけで、MemoryAgentがなぜ必要か伝わる。
```

やること:

- 合成メモリseedを増やす。不要、古い、重複、矛盾、慎重に扱うべき記憶を入れる。
- トークン削減率を視覚的に強くする。目標は60-75%削減。
- selected / demoted / contradicted / blocked の各判断に、短い理由を付ける。
- Raw Memoryは合成データで安全な形にしつつ、明確に失敗させる。
- ERINYS + Qwenは、その失敗を避けた回答にする。

完了条件:

- 同じ質問から、3つの回答の違いが明確に出る。
- Raw Memoryに古い情報や合成の個人識別情報が混ざる。
- ERINYS + Qwenは選ばれた記憶だけを使う。
- Memory Decisionsパネルを見れば、長い説明なしで差が分かる。

### フェーズ2: Qwen Cloud本接続を画面上でも主役にする

ゴール:

```text
ローカルだけのデモに見えない状態にする。
```

やること:

- UI上にQwen本接続ステータスを出し続ける。
- 実行メタデータを追加する。model、mode、base URL host、timestamp、token estimate。
- バックエンドでリクエスト単位のtrace IDを生成する。
- Qwen Cloudに繋がらない時の失敗表示を作る。秘密値は絶対に出さない。
- READMEを更新して、Qwen Cloud本接続モードの起動手順を明確にする。

完了条件:

- デモ動画内でQwen Cloud本接続ステータスが見える。
- READMEだけでローカル起動できる。
- UI、ログ、スクショ、docsに秘密値が出ない。

### フェーズ3: Alibaba Cloud証明を入れる

ゴール:

```text
インフラを作り込みすぎず、提出要件を満たす。
```

優先ルート:

- FastAPIバックエンドをAlibaba Cloud Function Compute、または同等のAlibaba Cloud実行環境に載せる。
- フロントエンドは無理にデプロイしない。必要なら静的ホスティングにする。
- リポジトリ内にAlibaba Cloudのサービス利用が分かるデプロイ設定やコードを置く。
- メイン動画とは別に、短い証明クリップを撮れる状態にする。

完了条件:

- 公開リポジトリにAlibaba Cloud向けのデプロイ設定やコードがある。
- 証明クリップでAlibaba Cloud上のバックエンド稼働が見える。
- メインデモはローカルUIでもよい。ただし、デプロイ証明との関係を説明できること。

### フェーズ4: 審査員向けに梱包する

ゴール:

```text
審査員が迷わず理解し、実行でき、採点できる状態にする。
```

やること:

- アーキテクチャ図を作る。
- 公開OSSリポジトリを作る。
- licenseファイルを追加する。
- `.env.example`、セットアップ手順、安全なモックモードを整える。
- READMEにJudging Mapを作る。機能と評価軸を対応させる。
- スクショを追加する。
- Devpost提出文を作る。

完了条件:

- 初見の審査員が数分でモックモードを起動できる。
- READMEにQwen本接続モードの説明がある。秘密値は出ない。
- アーキテクチャ図にfrontend、backend、ERINYS、memory seed/store、Qwen Cloud、Alibaba Cloud実行環境が入っている。

### フェーズ5: 動画を撮る

ゴール:

```text
3分で勝ち筋が分かる動画にする。
```

動画構成:

1. 0:00-0:20: 問題提起。長期エージェントは記憶しすぎる、古い記憶を引きずる、危ない記憶も拾う。
2. 0:20-0:45: 同じ質問に対する3つの回答を見せる。
3. 0:45-1:30: Raw Memoryの失敗を見せる。古い予定、矛盾、合成の個人ID。
4. 1:30-2:15: ERINYSの判断を見せる。selected、demoted、contradicted、blocked。
5. 2:15-2:40: Qwen本接続の回答が、選別済みcontextで改善するところを見せる。
6. 2:40-3:00: アーキテクチャとAlibaba Cloud / Qwen Cloud証明を見せる。

完了条件:

- YouTube、Vimeo、Facebook Videoのどれかで公開されている。
- 約3分に収まる。
- 動くUI、Qwen本接続ステータス、memory decisionsが見える。

## スケジュール

内部締切はJST。公式締切より前にバッファを置く。

| 日付 | 目標 |
| --- | --- |
| 2026-06-25 | 計画固定、Qwen本接続、デモ主張の固定 |
| 2026-06-26 | memory seed強化、answer diff強化 |
| 2026-06-27 | UI polish、run metadata追加 |
| 2026-06-28 | アーキテクチャ図、README Judging Map |
| 2026-06-29 | Alibaba Cloudデプロイルート決定、初回deploy |
| 2026-06-30 | デプロイ証明完成 |
| 2026-07-01 | 公開リポジトリ梱包 |
| 2026-07-02 | 動画台本、dry run |
| 2026-07-03 | 初回動画録画 |
| 2026-07-04 | デモと動画の穴を修正 |
| 2026-07-05 | 最終動画、提出文 |
| 2026-07-06 | Devpostに下書き提出 |
| 2026-07-07 | 外部目線でsanity check |
| 2026-07-08 | 最終固定 |
| 2026-07-10 06:00 | 公式締切 JST |

## 直近でやること

まずフェーズ1をやる。

次の具体タスク:

```text
合成メモリseedとscoringを強化して、Raw MemoryとERINYS + Qwenの差を審査員が一瞬で読める状態にする。
```

これを先にやる理由:

- Track 1の中心主張が強くなる。
- 動画が撮りやすくなる。
- Technical Depth、Innovation、Presentationの全部に効く。
- デモの芯が弱いままデプロイへ進むと、作業量だけ増えて勝ち筋がぼやける。
