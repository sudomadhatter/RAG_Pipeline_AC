import sys
from pathlib import Path

# Put `src/` on the path so tests can `from utils.schema import ...`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
