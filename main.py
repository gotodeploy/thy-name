import os

from fasthtml import (
    FastHTML,
    Link,
    Button,
    Table,
    Thead,
    Tr,
    Th,
    Td,
    Tbody,
)
from fasthtml.common import Div, H1, Main, Title, serve
from sqlalchemy import create_engine, select, update
from starlette.responses import FileResponse

from models import Kanji

engine = create_engine(
    os.environ["POSTGRES_URL"].replace("postgres://", "postgresql://")
)

app = FastHTML(
    hdrs=(
        Link(rel="stylesheet", href="assets/style.css"),
        Link(rel="stylesheet", href="fonts/NotoSerifTC-Regular.subset.woff2"),
        Link(rel="stylesheet", href="fonts/NotoSerifJP-Regular.subset.woff2"),
    )
)
rt = app.route


@rt("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f"public/{fname}.{ext}")


def rating(id, rating):
    return Td(
        f"{rating}讚",
        id=f"kanji_{id}",
    )


@rt("/kanji/downvote/{id}")
def post(id: int):
    with engine.connect() as connection:
        query = select(Kanji).where(Kanji.id == id)
        kanji = connection.execute(query).one()
        query = update(Kanji).values(rating=kanji.rating - 1).where(Kanji.id == id)
        connection.execute(query)
        connection.commit()

    return rating(id, kanji.rating - 1)


@rt("/kanji/upvote/{id}")
def post(id: int):
    with engine.connect() as connection:
        query = select(Kanji).where(Kanji.id == id)
        kanji = connection.execute(query).one()
        query = update(Kanji).values(rating=kanji.rating + 1).where(Kanji.id == id)
        connection.execute(query)
        connection.commit()

    return rating(id, kanji.rating + 1)


def draw_card(start, end):
    with engine.connect() as connection:
        query = select(Kanji).offset(start).limit(end).order_by(Kanji.rating.desc())
        for kanji in connection.execute(query).all():
            yield Tr(
                Td(
                    f"🇹🇼{kanji.character}",
                    cls="py-2 px-4 border-b, font-taiwan",
                ),
                Td(
                    f"🇯🇵{kanji.character}",
                    cls="py-2 px-4 border-b, font-nihon",
                ),
                rating(kanji.id, kanji.rating),
                Td(
                    Button(
                        "👍",
                        cls="bg-green-500 text-white px-2 py-1 rounded",
                        hx_post=f"/kanji/upvote/{kanji.id}",
                        hx_target=f"#kanji_{kanji.id}",
                        hx_swap="outerHTML",
                    ),
                    Button(
                        "👎",
                        cls="bg-red-500 text-white px-2 py-1 rounded",
                        hx_post=f"/kanji/downvote/{kanji.id}",
                        hx_target=f"#kanji_{kanji.id}",
                        hx_swap="outerHTML",
                    ),
                    cls="py-2 px-4 border-b",
                ),
            )


@rt("/")
def get():
    initial_cards = draw_card(0, 21)
    return Title("台灣日本命名可用漢字"), Main(
        H1("台灣日本命名可用漢字", cls="text-3xl mb-6"),
        Table(
            Thead(
                Tr(
                    Th("🇹🇼", cls="py-2 px-4 border-b"),
                    Th("🇯🇵", cls="py-2 px-4 border-b"),
                    Th("讚", cls="py-2 px-4 border-b"),
                    Th("", cls="py-2 px-4 border-b"),
                )
            ),
            Tbody(
                *initial_cards,
                Div(
                    hx_get="/more-cards",
                    hx_trigger="intersect once",
                    hx_swap="afterend",
                    hx_target="#container",
                ),
                id="container",
            ),
            cls="min-w-full bg-white border border-gray-200",
        ),
        cls="bg-gray-100 p-6 mx-auto",
    )


@rt("/more-cards")
def get(request):
    start = int(request.query_params.get("start", 21))
    end = start + 20

    new_cards = draw_card(start, end)

    if new_cards:
        return *new_cards, Div(
            hx_get=f"/more-cards?start={end}",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="this",
        )


serve()
