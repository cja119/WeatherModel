from setuptools import setup, find_packages

setup(
    name="meteor_py",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    package_data={
        'meteor_py': ['data/*.csv'],  # adjust as needed
    },
    install_requires = [
        "numpy==1.26.4",
        "pandas==2.2.2",
        "earthaccess==0.11.0",
        "xarray==2023.6.0",
        "cartopy==0.23.0",
        "shapely==2.0.6",
        "pysolar==0.11",
        "dill==0.3.9",
        "scipy==1.12.0",
        "h5netcdf==1.4.0"
        "netcdf4==1.7.2",
        "dask==2025.3.0"
    ]
)
