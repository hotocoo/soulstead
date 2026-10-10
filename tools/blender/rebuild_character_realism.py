"""Rebuild only the character assets through the full authored realism pipeline."""

import os
import sys
from pathlib import Path

os.environ["SOULSTEAD_ASSETS"] = "villager,gravewarden,ash_husk,cinder_stalker,echo"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import advance_soulstead_assets as pipeline


if __name__ == "__main__":
    pipeline.rebuild_all()
