"""Run a Memory Wrap script with SVHN files converted from the Hugging Face mirror.

The original Stanford download server is unreachable, so datasets/ holds .mat files
rebuilt from huggingface.co/datasets/ufldl-stanford/svhn. Their contents match the
official split sizes, but their MD5s differ, so torchvision's integrity check is skipped.

Usage (from paper/scripts): python ../run_with_local_svhn.py generate_memory_images.py --path_model ...
"""
import os
import runpy
import sys

import torchvision

torchvision.datasets.SVHN._check_integrity = lambda self: True
torchvision.datasets.SVHN.download = lambda self: None

script = sys.argv[1]
sys.argv = sys.argv[1:]
# Mimic `python script.py`: the script's own directory goes first on the import path.
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
runpy.run_path(script, run_name="__main__")
