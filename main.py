from fastapi import FastAPI
from user import routers


tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here ✨.",
    },
]

app = FastAPI(
    title="Kiosk API 👌",
    description="This is the Kiosk's API interactive documentation 😀",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.include_router(routers.router)
