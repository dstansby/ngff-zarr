from dataclasses import dataclass
from typing import List

from .ngff_image import NgffImage
from .zarr_metadata import Metadata

@dataclass
class Multiscale:
    images: List[NgffImage]
    metadata: Metadata
