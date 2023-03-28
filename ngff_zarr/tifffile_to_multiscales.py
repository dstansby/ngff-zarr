from typing import Any, Sequence, BinaryIO, Union
import os

def tifffile_to_multiscales(tiff_input: Union[str, os.PathLike[Any], BinaryIO, Sequence[Union[str, os.PathLike[Any]]], "tifffile.TiffFile", "tifffile.TiffSequence"]):
    import tifffile
    return multiscales