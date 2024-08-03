import csv
import random

from fasthtml import FastHTML, picolink, Link
from fasthtml.common import Div, H1, H2, Main, P, Path, Title, serve

app = FastHTML(
    hdrs=(
        picolink,
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=True),
        Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@200..900&family=Noto+Serif+TC:wght@200..900&display=swap",
        ),
    )
)


def load_csv(file_path: Path):
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


kanji = []
for row in load_csv(Path("data/common.csv")):
    for k, v in row.items():
        kanji.append(v)


def draw_card(number):
    color = f"hsl({random.randint(0, 360)}, 70%, 80%)"
    return Div(
        Div(
            H2(
                kanji[number],
                style='color: black; font-family: "Noto Serif TC", serif;"',
            ),
            P("🇹🇼"),
            cls="card",
            style=f"background-color: {color}; margin: 10px; padding: 20px; border-radius: 8px;",
        ),
        Div(
            H2(
                kanji[number],
                style='color: black; font-family: "Noto Serif JP", serif;"',
            ),
            P("🇯🇵"),
            cls="card",
            style=f"background-color: {color}; margin: 10px; padding: 20px; border-radius: 8px;",
        ),
        style="display:flex",
    )


@app.get("/")
def home():
    initial_cards = [draw_card(i) for i in range(1, 21)]
    return Title("台灣日本命名可用漢字"), Main(
        H1("台灣日本命名可用漢字"),
        Div(*initial_cards, id="card-container"),
        Div(
            hx_get="/more-cards",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="#card-container",
        ),
        style="max-width: 800px; margin: 0 auto;",
    )


@app.get("/more-cards")
def more_cards(request):
    start = int(request.query_params.get("start", 21))
    end = start + 20

    new_cards = [draw_card(i) for i in range(start, min(len(kanji), end))]

    if new_cards:
        return *new_cards, Div(
            hx_get=f"/more-cards?start={end}",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="this",
        )


serve()
