from ngff_zarr import Methods, multiscales_from_ngff_zarr
from zarr.storage import DirectoryStore
import zarr

from ._data import verify_against_baseline, test_data_dir


def test_gaussian_isotropic_scale_factors():
    dataset_name = 'cthead1'
    baseline_name = "2_4/DASK_IMAGE_GAUSSIAN.zarr"
    baseline_store = DirectoryStore(
        test_data_dir / f"baseline/{dataset_name}/{baseline_name}", dimension_separator="/"
    )
    root = zarr.group(baseline_store)
    # multiscales = multiscales_from_ngff_zarr(root)
    # verify_against_baseline(dataset_name, baseline_name, multiscales)

    # baseline_name = "auto/DASK_IMAGE_GAUSSIAN.zarr"
    # baseline_store = DirectoryStore(
    #     test_data_dir / f"baseline/{dataset_name}/{baseline_name}", dimension_separator="/"
    # )
    # root = zarr.group(baseline_store)
    # multiscales = multiscales_from_ngff_zarr(root)
    # verify_against_baseline(dataset_name, baseline_name, multiscales)