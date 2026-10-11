"""Generated tones for browser software tests ONLY; never competition speech data."""

import json
from pathlib import Path

import numpy as np
import soundfile as sf


def main():
    root = Path(__file__).resolve().parents[1] / "local-data/browser-fixtures"
    root.mkdir(parents=True, exist_ok=True)
    for role, frequency in [("reference", 220), ("participant", 260)]:
        time = np.arange(32000) / 16000
        samples = (0.2 * np.sin(2 * np.pi * frequency * time)).astype(np.float32)
        samples[8000:12000] = 0
        sf.write(root / f"generated-{role}.wav", samples, 16000, subtype="PCM_16")
    (root / "fixture-notice.json").write_text(
        json.dumps(
            {
                "origin": "generated signal software fixtures",
                "speech": False,
                "human_reviews": False,
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
