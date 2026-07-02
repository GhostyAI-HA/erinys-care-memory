# ERINYS CareDog Asset Canon

このアプリで使うERINYS CareDogの正本は、白い低ポリゴン調の介助犬です。

## Canonical Files

- `erinys-care-dog-source.png`
  - 緑背景付きの元画像。
  - 1485x1059 PNG、RGB。
- `erinys-care-dog.png`
  - アプリで参照する透明背景版。
  - 1485x1059 PNG、alpha付き。
- `erinys-care-dog-hero-960.webp` / `erinys-care-dog-hero-640.webp`
  - アプリ初期表示で使う軽量WebP版。
  - 960px版は約42KB、640px版は約24KB。
- `erinys-care-dog-hero-960.png`
  - WebP非対応環境向けの軽量PNG fallback。
  - `app/static/index.html` の `.care-dog` で使用する。

## Visual Identity

- 白い介助犬。
- ミント色のハーネス。
- 低ポリゴン/三角メッシュの体表。
- 家族の健康を見守る犬として見えること。
- 医療ケア、記憶ガバナンス、安全性を感じる見た目。

## Do Not Use

- 黒いダークなERINYS犬。
- 新規生成した別の犬。
- テキスト入り、ロゴ入り、バージョン番号入りの犬画像。

## Update Rule

CareDogを変える場合は、まずこのファイルを更新し、`erinys-care-dog-source.png` と
`erinys-care-dog.png` の両方を差し替える。会話ログだけを正本にしない。
