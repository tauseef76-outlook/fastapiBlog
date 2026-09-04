# Imports
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# Application Setup
app = FastAPI()


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template Configuration
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


# Data
POSTS = [
    {
        "id": 1,
        "title": "First Post",
        "content": "This is the content of the first post.",
    },
    {
        "id": 2,
        "title": "Second Post",
        "content": "This is the content of the second post.",
    },
    {
        "id": 3,
        "title": "Third Post",
        "content": "This is the content of the third post.",
    },
]


def render_error(
    request: Request,
    status_code: int,
    title: str,
    message: str,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "request": request,
            "status_code": status_code,
            "title": title,
            "message": message,
        },
        status_code=status_code,
    )


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return render_error(
        request,
        status.HTTP_418_IM_A_TEAPOT,
        "A unicorn error occurred",
        f"Oops! {exc.name} did something unexpected.",
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return render_error(
        request,
        exc.status_code,
        "Request error",
        str(exc.detail),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, _exc: RequestValidationError):
    logger.warning(
        "Request validation failed for %s: %d error(s)",
        request.url.path,
        len(_exc.errors()),
    )
    return render_error(
        request,
        422,
        "Invalid request",
        "Please check the request data and try again.",
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, _exc: Exception):
    logger.exception(
        "Unhandled exception while processing %s: %s",
        request.url.path,
        _exc,
    )
    return render_error(
        request,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Something went wrong",
        "The server could not complete your request. Please try again.",
    )


# Routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request, "posts": POSTS},
    )


@app.get("/post/{id}", response_class=HTMLResponse)
def post_detail(request: Request, id: int):
    for post in POSTS:
        if id == post["id"]:
            return templates.TemplateResponse(
                request, "posts.html", {"request": request, "post": post}
            )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "request": request,
            "status_code": status.HTTP_404_NOT_FOUND,
            "title": "Post not found",
            "message": f"We could not find a post with ID {id}.",
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )
    # raise UnicornException(name="Post not found")
    # return {"unicorn_name": name}

    # post = next((post for post in POSTS if post["id"] == id), None)
    # if post is None:
    #     return templates.TemplateResponse(
    #         request, "404.html", {"request": request}, status_code=404
    #     )
    # return templates.TemplateResponse(
    #     request, "post_detail.html", {"request": request, "post": post}
    # )


# @app.get("/items/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     return templates.TemplateResponse(
#         request=request, name="item.html", context={"id": id}
#     )
