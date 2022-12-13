import zarr
from typing import List
import dask.array as da

from .multiscale import Multiscale
from .zarr_metadata import Metadata
from .to_ngff_image import to_ngff_image

def multiscales_from_ngff_zarr(root: zarr.Group) -> List[Multiscale]:
    """
    Load an ngff_zarr.Multiscales in memory representation of an NGFF Zarr store.
    """

    # metadata = Metadata(**root.attrs['multiscales'][0])
    metadata_dict = dict(**root.attrs['multiscales'][0])
    metadata_dict.pop('@type', None)
    metadata = Metadata(**metadata_dict)

    print(metadata)
    images = []
    for index, image in enumerate(metadata.datasets):
        path = metadata.datasets[index]['path']
        data = da.from_zarr(root, path)
        image = to_ngff_image(data)
        images.append(image)
    
    return multiscales