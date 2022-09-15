import asyncio
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


class RelativePathFilter(logging.Filter):
    def filter(self, record):
        path = Path(record.pathname).resolve()
        record.relativepath = str(path.relative_to(REPO_ROOT))
        return True


def jprint(o):
    print(json.dumps(o, indent=2, default=str))


def sprint(*args):
    print(*args, file=sys.stderr)


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


def init_log():
    logging.basicConfig(
        format="[%(relativepath)s:%(lineno)d %(levelname)-1s] %(message)s",
        level=logging.WARN,
    )

    # Flush on every log call (logging and then calling subprocess.run can make
    # the output look confusing)
    logging.root.handlers[0].addFilter(RelativePathFilter())
    logging.root.handlers[0].flush = sys.stderr.flush
