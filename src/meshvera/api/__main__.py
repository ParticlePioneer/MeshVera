"""`python -m meshvera.api` starts the API with validated settings."""

import uvicorn

from meshvera.api.main import create_app
from meshvera.config import load_settings_or_exit


def main() -> None:
    settings = load_settings_or_exit()
    uvicorn.run(create_app(settings), host=settings.api_host, port=settings.api_port)


if __name__ == "__main__":
    main()
