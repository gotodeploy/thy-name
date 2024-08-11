import os

from fasthtml import setup_toasts, add_toast
from fasthtml.common import (
    Button,
    Div,
    FastHTML,
    Form,
    H1,
    Input,
    Link,
    Main,
    Svg,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Title,
    Tr,
    serve,
)
from fasthtml.svg import Path
from sqlalchemy import create_engine, select, update, insert, func
from starlette.responses import FileResponse

from models import Kanji, ThyName

CHUNK_SIZE = 20

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
setup_toasts(app)
rt = app.route


@rt("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f"public/{fname}.{ext}")


def rating_tag(id, rating):
    return Td(
        f"{rating}讚",
        id=id,
        cls="py-2 px-4 border-b",
    )


def vote_rating(model, model_id: int, rating: int):
    with engine.connect() as connection:
        query = select(model).where(model.id == model_id)
        target = connection.execute(query).one()
        new_rating = target.rating + rating
        query = update(model).values(rating=new_rating).where(model.id == model_id)
        connection.execute(query)
        connection.commit()

    return new_rating


def refresh_button(active_tab):
    return (
        Div(
            Button(
                Svg(
                    Path(
                        **{
                            "stroke-linecap": "round",
                            "stroke-linejoin": "round",
                            "stroke-width": "2",
                            "d": """M460.656,132.911c-58.7-122.1-212.2-166.5-331.8-104.1c-9.4,5.2-13.5,16.6-8.3,27c5.2,9.4,16.6,13.5,27,8.3
    		c99.9-52,227.4-14.9,276.7,86.3c65.4,134.3-19,236.7-87.4,274.6c-93.1,51.7-211.2,17.4-267.6-70.7l69.3,14.5
    		c10.4,2.1,21.8-4.2,23.9-15.6c2.1-10.4-4.2-21.8-15.6-23.9l-122.8-25c-20.6-2-25,16.6-23.9,22.9l15.6,123.8
    		c1,10.4,9.4,17.7,19.8,17.7c12.8,0,20.8-12.5,19.8-23.9l-6-50.5c57.4,70.8,170.3,131.2,307.4,68.2
    		C414.856,432.511,548.256,314.811,460.656,132.911z""",
                        }
                    ),
                    fill="#EEEEEE",
                    viewBox="0 0 489.645 489.645",
                    stroke="currentColor",
                    cls="h-6 rounded text-white",
                ),
                hx_get=active_tab,
                hx_trigger="click",
                hx_swap="innerHTML",
                hx_target="#container",
                cls="inline-flex items-center px-2 py-2 bg-green-500 aspect-square rounded-full",
            ),
        ),
    )


def vote_buttons(model, id, tag):
    return Td(
        Button(
            "👍",
            cls="bg-green-500 text-white px-2 py-1 rounded",
            hx_post=f"/{model}/upvote/{id}",
            hx_target=tag,
            hx_swap="outerHTML",
        ),
        Button(
            "👎",
            cls="bg-red-500 text-white px-2 py-1 rounded",
            hx_post=f"/{model}/downvote/{id}",
            hx_target=tag,
            hx_swap="outerHTML",
        ),
        cls="py-2 px-4 border-b",
    )


@rt("/kanji/downvote/{kanji_id}")
def post(kanji_id: int):
    new_rating = vote_rating(Kanji, kanji_id, -1)
    return rating_tag(f"kanji_{kanji_id}", new_rating)


@rt("/kanji/upvote/{kanji_id}")
def post(kanji_id: int):
    new_rating = vote_rating(Kanji, kanji_id, +1)
    return rating_tag(f"kanji_{kanji_id}", new_rating)


@rt("/")
def get():
    return Title("台灣日本命名可用漢字"), Main(
        H1("台灣日本命名可用漢字", cls="text-3xl mb-6"),
        Div(
            *page("kanji"),
            id="container",
        ),
        cls="bg-gray-100 p-6 mx-auto",
    )


def header_tab(activate):
    cls_active = "bg-blue-500 text-white px-4 py-2 rounded"
    cls_inactive = "bg-gray-300 text-gray-700 px-4 py-2 rounded"
    tab_attributes = {
        "漢字評分": {"hx_get": "/kanji-board", "cls": cls_inactive},
        "名字評分": {"hx_get": "/name-board", "cls": cls_inactive},
    }
    match activate:
        case "kanji":
            tab_attributes["漢字評分"]["cls"] = cls_active
            active_tab = "/kanji-board"
        case "name":
            tab_attributes["名字評分"]["cls"] = cls_active
            active_tab = "/name-board"
        case _:
            tab_attributes["漢字評分"]["cls"] = cls_active
            active_tab = "/kanji-board"

    tabs = (
        Button(
            label,
            hx_trigger="click",
            hx_swap="innerHTML",
            hx_target="#container",
            **attributes,
        )
        for label, attributes in tab_attributes.items()
    )
    return Div(
        Div(
            tabs,
            cls="flex space-x-4",
        ),
        refresh_button(active_tab),
        cls="flex justify-between items-center pb-3 mb-4",
    )


def draw_kanji(offset, kanji_count):
    with engine.connect() as connection:
        query = (
            select(Kanji)
            .offset(offset)
            .fetch(kanji_count)
            .order_by(Kanji.rating.desc(), Kanji.id.asc())
        )
        for kanji in connection.execute(query).all():
            kanji_tag = f"kanji_{kanji.id}"
            yield Tr(
                Td(
                    f"🇹🇼{kanji.character}",
                    cls="py-2 px-4 border-b font-taiwan",
                ),
                Td(
                    f"🇯🇵{kanji.character}",
                    cls="py-2 px-4 border-b font-nihon",
                ),
                rating_tag(kanji_tag, kanji.rating),
                vote_buttons("kanji", kanji.id, f"#{kanji_tag}"),
            )


def kanji_board():
    initial_cards = draw_kanji(0, CHUNK_SIZE)
    headers = ("🇹🇼", "🇯🇵", "讚", "")
    return (
        Table(
            Thead(Tr(Th(header, cls="py-2 px-4 border-b") for header in headers)),
            Tbody(
                *initial_cards,
                Div(
                    hx_get="/more-kanji",
                    hx_trigger="intersect once",
                    hx_swap="afterend",
                    hx_target="#kanji_container",
                ),
                id="kanji_container",
            ),
            cls="min-w-full bg-white border border-gray-200",
        ),
    )


@rt("/more-kanji")
def get(request):
    offset = int(request.query_params.get("start", CHUNK_SIZE))
    new_cards = draw_kanji(offset, CHUNK_SIZE)

    if new_cards:
        return *new_cards, Div(
            hx_get=f"/more-kanji?start={offset + CHUNK_SIZE}",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="this",
        )


@rt("/kanji-board")
def get():
    return page("kanji")


@rt("/name/downvote/{name_id}")
def post(name_id: int):
    new_rating = vote_rating(ThyName, name_id, -1)
    return rating_tag(f"name_{name_id}", new_rating)


@rt("/name/upvote/{name_id}")
def post(name_id: int):
    new_rating = vote_rating(ThyName, name_id, +1)
    return rating_tag(f"name_{name_id}", new_rating)


def draw_name(offset, name_count):
    with engine.connect() as connection:
        query = (
            select(ThyName)
            .offset(offset)
            .fetch(name_count)
            .order_by(ThyName.rating.desc(), ThyName.id.desc())
        )
        items = []
        for name in connection.execute(query).all():
            name_tag = f"name_{name.id}"
            items.append(
                Tr(
                    Td(
                        f"{name.name}",
                        cls="py-2 px-4 border-b font-taiwan",
                    ),
                    rating_tag(name_tag, name.rating),
                    vote_buttons("name", name.id, f"#{name_tag}"),
                )
            )
        return items


def validate_name(name):
    normalized_name = set(name)
    with engine.connect() as connection:
        query = (
            select(func.count("id"))
            .select_from(Kanji)
            .where(Kanji.character.in_(normalized_name))
        )
        kanji_count = connection.execute(query).scalar()
        return kanji_count != len(normalized_name)


@rt("/register-name")
async def put(session, request):
    request_json = await request.form()
    input_name = request_json.get("name")
    if not input_name:
        return
    if validate_name(input_name):
        add_toast(session, f'"{input_name}" 輸入有誤', "error")
        return
    with engine.connect() as connection:
        query = insert(ThyName).values(name=input_name)
        connection.execute(query)
        connection.commit()
        query = select(ThyName).where(ThyName.name == input_name)
        registered_name = connection.execute(query).one()

    name_tag = f"name_{registered_name.id}"
    return Tr(
        Td(
            f"{registered_name.name}",
            cls="py-2 px-4 border-b font-taiwan",
        ),
        rating_tag(name_tag, registered_name.rating),
        vote_buttons("name", registered_name.id, f"#{name_tag}"),
    )


@rt("/more-name")
def get(request):
    offset = int(request.query_params.get("start", CHUNK_SIZE))

    new_cards = draw_name(offset, CHUNK_SIZE)

    if new_cards:
        return *new_cards, Div(
            hx_get=f"/more-name?start={offset + CHUNK_SIZE}",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="this",
        )


def name_board():
    initial_cards = draw_name(0, CHUNK_SIZE)
    return (
        Div(
            Form(
                Input(
                    type="text",
                    name="name",
                    placeholder="名字",
                    cls="border border-gray-300 p-2 rounded-lg w-full",
                ),
                Button(
                    "提出",
                    type="submit",
                    hx_put="/register-name",
                    hx_trigger="click",
                    hx_swap="afterbegin",
                    hx_target="#name_container",
                    hx_include="previous [name='name']",
                    cls="bg-blue-500 text-white px-4 py-2 rounded-lg whitespace-nowrap",
                ),
                hx_on__after_request="this.reset()",
                cls="flex space-x-4",
            ),
            cls="mb-6",
        ),
        Table(
            Thead(
                Tr(
                    Th("🐣", cls="py-2 px-4 border-b"),
                    Th("讚", cls="py-2 px-4 border-b"),
                    Th("", cls="py-2 px-4 border-b"),
                )
            ),
            Tbody(
                *initial_cards,
                Div(
                    hx_get="/more-name",
                    hx_trigger="intersect once",
                    hx_swap="afterend",
                    hx_target="#name_container",
                ),
                id="name_container",
            ),
            cls="min-w-full bg-white border border-gray-200",
        ),
    )


@rt("/name-board")
def get():
    return page("name")


def page(activate):
    match activate:
        case "kanji":
            return header_tab("kanji"), kanji_board()
        case "name":
            return header_tab("name"), name_board()


serve()
