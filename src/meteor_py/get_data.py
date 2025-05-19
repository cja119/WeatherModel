""" """

from pathlib import Path
from glob import glob


class GetData:
    def __init__(self, keys):
        targ = Path(__file__).parent / "data"
        self._data = []
        for file_name in keys:
            csvs_files = glob(str(targ / file_name))

        for file_name in csvs_files:
            with open(file_name) as f:
                next(f)
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        _, value = parts
                    elif len(parts) == 1:
                        value = float(parts[0])
                    self._data.extend([float(value)])

    def data(self):
        return self._data
