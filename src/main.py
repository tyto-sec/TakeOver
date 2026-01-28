import logging
import os

from tasks import run

def main():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    run()


if __name__ == '__main__':
    main()