import asyncio
import logging

from app.scheduler import configure_logging, run_cycle


def main() -> None:
    configure_logging()
    logging.getLogger(__name__).info("Running single finance news cycle...")
    asyncio.run(run_cycle())


if __name__ == "__main__":
    main()
