"""Root launcher: `uv run python main.py` runs the app in src/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import chat  # noqa: E402  (src/main.py)

if __name__ == "__main__":
    chat()
