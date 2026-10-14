"""Run the current all-choice and AI audio browser regressions. Server :4173 required."""
import runpy
from pathlib import Path
for name in ['choice_test.py','audio_test.py']:
    runpy.run_path(str(Path(__file__).with_name(name)),run_name='__main__')
