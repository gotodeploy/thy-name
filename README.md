# 台灣日本命名可用漢字

## 數據集

- [kanji-data](https://github.com/mimneko/kanji-data) - 日本命名可用漢字
  - `人名漢字.csv`
  - `常用漢字.csv`
- [教育部4808個常用字](https://ws.moe.edu.tw/001/Upload/6/relfile/7856/42276/31104e65-ead1-4320-b6c6-d0f444296a7e.pdf) - 篩選並排除非一般常用漢字
  - `教育部4808個常用字.xls`
- [UCS strokes](https://github.com/cjkvi/cjkvi-ids/) - 篩選漢字筆畫數
  - `ucs-strokes.txt`
- [Noto Sans Traditional Chinese](https://fonts.google.com/noto/specimen/Noto+Sans+TC) - 繁體字字型
  - `NotoSerifTC-Regular.ttf`

## Commands

- Create new revision

```shell
docker compose exec app alembic revision --autogenerate -m "comment"
```

- Run migration online

```shell
POSTGRES_URL=postgresql:// alembic upgrade head
```

- Generate offset font

```shell
docker compose exec app pyftsubset public/fonts/NotoSerifTC-Regular.ttf --no-hinting --flavor=woff2 --text-file=migrations/seeds/kanji.csv
```