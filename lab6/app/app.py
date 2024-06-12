from typing import Annotated

import aiohttp
from configuration import static_router, template_config
from litestar import Litestar, get, post
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template


@get("/")
async def index() -> Template:
    return HTMXTemplate(template_name="index.html")


@post("/qr")
async def qr(
    data: Annotated[dict[str, str], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Template:
    async with (
        aiohttp.ClientSession() as session,
        session.post(
            "https://ci5z03azn2.execute-api.us-east-1.amazonaws.com",
            json={"toEncode": data["to-encode"]},
        ) as response,
    ):
        try:
            response_data = await response.json()
            message = response_data["message"]
            if message == "QR code generated":
                return HTMXTemplate(
                    template_name="qr.html",
                    context={"link": response_data["link"]},
                )
            return HTMXTemplate(
                template_name="error.html",
                re_target="main",
                context={"message": message},
            )
        except Exception as e:  # noqa: BLE001
            return HTMXTemplate(
                template_name="error.html",
                re_target="main",
                context={"message": str(e)},
            )


app = Litestar(
    route_handlers=[
        static_router,
        index,
        qr,
    ],
    template_config=template_config,
)
