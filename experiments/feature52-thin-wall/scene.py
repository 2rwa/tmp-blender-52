from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments._shared.showcase52 import run
run("feature52-thin-wall")
