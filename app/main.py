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
    return 'Hello, <a href="https://scnuoss.net/">https://scnuoss.net/</a>'


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("INTERNAL_HOST", "127.0.0.1"),
        port=int(os.getenv("INTERNAL_PORT", "8000")),
    )
