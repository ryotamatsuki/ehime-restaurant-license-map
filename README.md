# Ehime Restaurant License Map

愛媛県・松山市のオープンデータ「食品営業許可」から、飲食店等の新規営業許可の時空間変化を再現・可視化するプロジェクトです。

## 目的

「現在どこに店があるか」ではなく、営業許可が **いつ・どこで新たに発生したか** を月次で復元し、愛媛県内の飲食店立地の変化をインタラクティブな地図・アニメーションで観察できる状態を目指します。

> 注意: 営業許可は開店・閉店そのものと同義ではありません。全施設一覧には休止・廃業施設が含まれる場合があります。本プロジェクトでは原則として「新規営業許可の発生」と表現します。

## Project stages

| Stage | 内容 | Exit criteria |
|---|---|---|
| 0 | Repository / data governance | 構成、ライセンス、PII除外方針、再現手順を固定 |
| 1 | Source discovery | 愛媛県・松山市の公式データソースと更新仕様を確定 |
| 2 | Acquisition & schema audit | 現行データを取得し、シート・列・型・件数・欠損を監査 |
| 3 | Historical reconstruction | 取得可能な月次履歴を探索・収集し、時系列パネルを構築 |
| 4 | Geocoding | 住所正規化、緯度経度付与、品質フラグ付与 |
| 5 | Spatial metrics | 市町・メッシュ・hexbin・KDE等の集積指標を生成 |
| 6 | Interactive visualization | 時間スライダー、Points / Heatmap / Hexagon等を実装 |
| 7 | Publication | GitHub Pages公開、出典・免責・再現性QA |

詳細は [`PROJECT_PLAN.md`](PROJECT_PLAN.md) を参照してください。

## Data policy

このリポジトリは公開を前提とします。

- 公式データからの**分析に不要な申請者氏名、申請者カナ、電話番号等はGitに保存しません**。
- 公式原本は取得処理中の一時ファイルとして扱い、原則 `.gitignore` 対象とします。
- Gitに保存するのは、分析に必要な列へ限定したスナップショット、取得元URL、取得日時、SHA-256、ライセンス、変換ログです。
- 2026年8月に愛媛県公開データで誤掲載事案があったため、当該期間に取得された問題ファイルは使用・保存しません。
- 可視化上の表現は「店舗の開閉」ではなく、データで確認可能な「営業許可の発生」を基本とします。

## Official sources

- 愛媛県オープンデータ「食品営業許可施設一覧」: 松山市を除く県内。月1回更新。
- 松山市オープンデータ「食品営業許可新規又は更新施設一覧」: 過去1年、新規又は更新を月1回更新。
- 松山市オープンデータ「食品営業許可全施設一覧」: 年1回更新。

出典・取得仕様は [`config/sources.yaml`](config/sources.yaml)、調査記録は [`docs/research/SOURCE_AUDIT.md`](docs/research/SOURCE_AUDIT.md) に記録します。

## Repository layout

```text
.
├── config/
│   └── sources.yaml
├── data/
│   ├── README.md
│   ├── snapshots/
│   └── processed/
├── docs/
│   └── research/
├── src/
│   ├── acquire/
│   ├── transform/
│   └── audit/
└── .github/workflows/
```

## Status

Stage 0: in progress  
Stage 1: in progress  
Stage 2: in progress
