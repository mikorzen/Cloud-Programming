from typing import Annotated

import aiohttp
import boto3
from configuration import create_database, static_router, template_config
from litestar import Litestar, Response, get, post
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template
from models.file_upload import FileUpload

s3 = boto3.resource("s3")
bucket = s3.Bucket("bucket-djsklfh34ltn85439erhgjwe")
connection, cursor = create_database()


@get("/")
async def index() -> Template:
    return HTMXTemplate(template_name="index.html")


@get("/files")
async def files() -> Template:
    cursor.execute("SELECT * FROM file")
    files = [dict(row) for row in cursor.fetchall()]
    return HTMXTemplate(template_name="files.html", context={"files": files})


@post("/upload")
async def upload(
    data: Annotated[FileUpload, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Redirect:
    name = data.name
    file = data.file
    content = await file.read()

    bucket.put_object(Key=name, Body=content, ACL="public-read")
    cursor.execute(
        "INSERT INTO file (name, link) VALUES (?, ?)",
        (name, f"https://bucket-djsklfh34ltn85439erhgjwe.s3.amazonaws.com/{name}"),
    )
    connection.commit()

    return Redirect("/files")


@get("/download/{file_id:int}", media_type="text/plain")
async def download(file_id: int) -> Response:
    cursor.execute("SELECT * FROM file WHERE id = ?", (file_id,))
    file = cursor.fetchone()
    async with aiohttp.ClientSession() as session:  # noqa: SIM117
        async with session.get(file["link"]) as response:
            file_content = await response.read()

    return Response(
        content=file_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{file["name"]}"'},
    )


@get("/edit/{file_id:int}")
async def edit(file_id: int, name: str) -> Redirect:
    cursor.execute("UPDATE file SET name = ? WHERE id = ?", (name, file_id))
    connection.commit()

    return Redirect("/files")


@get("/delete/{file_id:int}")
async def delete(file_id: int) -> Redirect:
    cursor.execute("SELECT * FROM file WHERE id = ?", (file_id,))
    file = cursor.fetchone()
    file_name = file["link"].split("/")[-1]
    bucket.Object(file_name).delete()
    cursor.execute("DELETE FROM file WHERE id = ?", (file_id,))
    connection.commit()

    return Redirect("/files")


app = Litestar(
    route_handlers=[
        static_router,
        index,
        files,
        upload,
        download,
        edit,
        delete,
    ],
    template_config=template_config,
)
