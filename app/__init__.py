from pathlib import Path
from pkgutil import extend_path

# Allow imports like `app.*` to resolve whether the server is launched
# from the repository root or from the `backend` directory.
__path__ = extend_path(__path__, __name__)

backend_app_dir = Path(__file__).resolve().parent.parent / "backend" / "app"
backend_app_dir_str = str(backend_app_dir)

if backend_app_dir.is_dir() and backend_app_dir_str not in __path__:
    __path__.append(backend_app_dir_str)
