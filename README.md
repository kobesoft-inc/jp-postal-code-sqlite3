# jp-postal-code-sqlite3

日本郵便が公開している郵便番号データ（KEN_ALL）をダウンロードし、SQLite3データベースに変換するツールです。

## 使い方

Python 3系のみで動作します（追加の依存ライブラリは不要です）。

```bash
python3 build_db.py -o jp_postal_code.db
```

実行すると、日本郵便のサイトから最新の郵便番号データ（UTF-8版CSV）をダウンロードし、
カレントディレクトリに `jp_postal_code.db` を生成します。

## データソース

- 日本郵便 郵便番号データダウンロード（UTF-8版）
  https://www.post.japanpost.jp/zipcode/dl/utf-zip.html

## テーブル構成

`postal_codes` テーブル（列の意味は日本郵便のKEN_ALL仕様に準拠）

| カラム | 内容 |
| --- | --- |
| jis_code | 全国地方公共団体コード |
| old_zip_code | 旧郵便番号（5桁） |
| zip_code | 郵便番号（7桁） |
| pref_kana / city_kana / town_kana | 都道府県名・市区町村名・町域名（カナ） |
| pref / city / town | 都道府県名・市区町村名・町域名 |
| is_multi_zip | 一町域が二以上の郵便番号で表される場合 |
| has_koaza_banchi | 小字毎に番地が起番されている町域 |
| has_chome | 丁目を有する町域 |
| is_multi_town | 一つの郵便番号で二以上の町域を表す場合 |
| update_flag | 更新の表示（0:変更なし, 1:変更あり, 2:廃止） |
| change_reason | 変更理由 |

`zip_code` にインデックスを作成しているため、郵便番号による検索は高速に行えます。

```sql
SELECT pref, city, town FROM postal_codes WHERE zip_code = '1000001';
```

## ライセンス

このリポジトリのコードは MIT License です。
郵便番号データ自体の利用条件は日本郵便の定める規約に従います。
