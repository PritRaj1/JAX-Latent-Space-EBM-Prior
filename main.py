import os

os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.95"
# os.environ["JAX_DISABLE_JIT"] = "True"

import numpy as np
import torch
import configparser
import tqdm

from src.utils.helper_functions import get_data, NumpyLoader
from src.experiment import run_experiment

parser = configparser.ConfigParser()
parser.read("hyperparams.ini")

data_set_name = parser["PIPELINE"]["DATASET"]
num_train_data = int(parser["PIPELINE"]["NUM_TRAIN_DATA"])
num_val_data = int(parser["PIPELINE"]["NUM_VAL_DATA"])
batch_size = int(parser["PIPELINE"]["BATCH_SIZE"])
num_exp = int(parser["PIPELINE"]["NUM_EXPERIMENTS"])
temp_power = int(parser["TEMP"]["TEMP_POWER"])
dataset, val_dataset = get_data(data_set_name)

# Take a subset of the dataset to ease computation
train_data = torch.utils.data.Subset(dataset, range(num_train_data))
val_data = torch.utils.data.Subset(val_dataset, range(num_val_data))

# Split dataset
train_loader = NumpyLoader(train_data, batch_size=batch_size, shuffle=True)
val_loader = NumpyLoader(val_data, batch_size=batch_size, shuffle=False)
train_x = np.stack([x for x, _ in train_loader])
val_x = np.stack([x for x, _ in val_loader])
del val_loader, train_loader, train_data, val_data

log_path = f"logs/{data_set_name}/p={temp_power}/batch={batch_size}"
os.makedirs(f"{log_path}/images", exist_ok=True)

for exp in tqdm.tqdm(range(2, num_exp)):
    run_experiment(exp, train_x, val_x, log_path)
