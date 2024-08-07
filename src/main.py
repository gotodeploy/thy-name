import os
import random

from fasthtml import FastHTML, picolink, Link
from fasthtml.common import Div, H1, H2, Main, P, Title, serve
from sqlalchemy import create_engine, select

from src.models import Kanji

kanji = []

engine = create_engine(os.environ["POSTGRES_URL"])
with engine.connect() as connection:
    for record in connection.execute(select(Kanji.character)).all():
        kanji.append(record.character)


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


def draw_card(number):
    color = f"hsl({random.randint(0, 360)}, 70%, 80%)"
    return Div(
        Div(
            H2(
                kanji[number],
                style='color: black; font-variant-east-asian: traditional; font-family: "Noto Serif TC", serif;"',
            ),
            P("🇹🇼"),
            cls="card",
            style=f"background-color: {color}; margin: 10px; padding: 20px; border-radius: 8px;",
        ),
        Div(
            H2(
                kanji[number],
                style='color: black; font-variant-east-asian: jis04; font-family: "Noto Serif JP", serif;"',
            ),
            P("🇯🇵"),
            cls="card",
            style=f"background-color: {color}; margin: 10px; padding: 20px; border-radius: 8px;",
        ),
        style="display:flex",
    )


@app.get("/")
def home():
    initial_cards = [draw_card(i) for i in range(0, 21)]
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
    start = int(request.query_params.get("start", 20))
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
