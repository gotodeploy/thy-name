import csv
from pathlib import Path

from sqlalchemy import insert

from models import Kanji


def load_csv(file_path: Path):
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def insert_kanji(session, file_path="./migrations/seeds/kanji.csv"):
    characters = list(load_csv(Path(file_path)))
    session.execute(insert(Kanji), characters)
