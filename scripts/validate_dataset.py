import sys

from _paths import PROJECT_ROOT
from experiments.dataset_validator import DatasetValidator

dataset_name = sys.argv[1]

validator = DatasetValidator(str(PROJECT_ROOT / "datasets" / dataset_name))

results = validator.run()

for r in results:
    print(r)
