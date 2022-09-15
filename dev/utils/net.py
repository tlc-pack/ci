import logging
import os
import subprocess
from pathlib import Path

import requests

CACHE_DIR = None
DEBUG = os.getenv("DEBUG", "0") == "1"


def init(dir):
    global CACHE_DIR
    CACHE_DIR = Path(os.getcwd()).resolve() / dir
    CACHE_DIR.mkdir(exist_ok=True, parents=True)


def get(url, *args, **kwargs):
    use_cache = kwargs.pop("use_cache", True)

    cache_name = url.replace("/", "-")
    cached = CACHE_DIR / cache_name
    if cached.exists() and use_cache:
        with open(cached, "rb") as f:
            return f.read()
    else:
        checker = kwargs.pop("is_fresh", None)
        result = requests.get(url, *args, **kwargs)
        content = result.content.decode()
        if checker is None or checker(url, content):
            with open(cached, "w") as f:
                f.write(content)
        return content


def curl(url):
    proc = subprocess.run(["curl", "-L", url], stdout=subprocess.PIPE, check=True)
    return proc.stdout.decode()


async def aioget(url, session, use_cache=True):
    if DEBUG:
        use_cache = True
    cache_name = url.replace("/", "-")
    cached = CACHE_DIR / cache_name
    if cached.exists() and use_cache:
        logging.info(f"GET {url} [cached]")
        with open(cached, "r") as f:
            return f.read()
    else:
        if use_cache:
            logging.info(f"GET {url} [cache miss]")
        else:
            logging.info(f"GET {url} [cache disabled]")
        result = await session.get(url)
        text = await result.text()
        with open(cached, "w") as f:
            f.write(text)
        return text


async def aiogetc(url, session, use_cache=True):
    if DEBUG:
        use_cache = True
    cache_name = url.replace("/", "-")
    cached = CACHE_DIR / cache_name
    if cached.exists() and use_cache:
        logging.info(f"GET {url} [cached]")
        with open(cached, "r") as f:
            return f.read(), 200
    else:
        if use_cache:
            logging.info(f"GET {url} [cache miss]")
        else:
            logging.info(f"GET {url} [cache disabled]")
        result = await session.get(url)
        text = await result.text()
        with open(cached, "w") as f:
            f.write(text)
        return text, result.status_code
