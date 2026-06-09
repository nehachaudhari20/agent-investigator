import sys

from experiments.dataset_validator import (
    DatasetValidator
)

dataset_name = sys.argv[1]

validator = DatasetValidator(
    f"datasets/{dataset_name}"
)

results = validator.run()

for r in results:
    print(r)