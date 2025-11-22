import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path when executed as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scheduler import configure_logging, run_cycle


def main() -> None:
    configure_logging()
    logging.getLogger(__name__).info("Running single finance news cycle...")
    asyncio.run(run_cycle())


if __name__ == "__main__":
    main()
