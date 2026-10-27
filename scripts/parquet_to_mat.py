"""Convert Hugging Face SVHN parquet files into the .mat layout torchvision.datasets.SVHN reads."""
import io
import sys

import numpy as np
import pyarrow.parquet as pq
import scipy.io
from PIL import Image

src_dir, dst_dir = sys.argv[1], sys.argv[2]
for split in ("train", "test"):
    table = pq.read_table(f"{src_dir}/{split}.parquet").to_pydict()
    imgs = np.stack([np.array(Image.open(io.BytesIO(im["bytes"])).convert("RGB")) for im in table["image"]])
    labels = np.array(table["label"], dtype=np.uint8)
    labels[labels == 0] = 10  # original SVHN .mat files label digit 0 as 10
    scipy.io.savemat(f"{dst_dir}/{split}_32x32.mat", {"X": imgs.transpose(1, 2, 3, 0), "y": labels.reshape(-1, 1)})
    print(split, imgs.shape, np.bincount(labels)[1:])
