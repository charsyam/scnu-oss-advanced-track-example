import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def hello():
    return """<!doctype html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>순천대학교 OSS 해커톤</title>
</head>
<body>
    Hello, <a href="https://scnuoss.net/">https://scnuoss.net/</a>
</body>
</html>"""


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("INTERNAL_HOST", "127.0.0.1"),
        port=int(os.getenv("INTERNAL_PORT", "8000")),
    )
