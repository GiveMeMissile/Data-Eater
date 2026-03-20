import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# File Constants:
DATA = "Data"  # Data Saving Folder Name
PARQUET = DATA + "/" + "Parquet"
CSV = DATA + "/" + "CSV"
SQLITE = DATA + "/" + "SQLite"
JSONL = DATA + "/" + "JSONL"

# Options Constants:
NUM_SAMPLE_STEPS = config["gui"]["steps"]
MIN_BI = config["gui"]["min_bi_encoding"]
MAX_BI = config["gui"]["max_bi_encoding"]
DEFAULT_BI = config["gui"]["default_bi_encoding"]
MAX_INPUT = config["gui"]["max_input_box"]
MIN_INPUT = config["gui"]["min_input_box"]
DEFAULT_INPUT = config["gui"]["default_input_box"]

# AI Model Options:
BI_ENCODER_MODEL = config["bi_encoder_model_name"]
CROSS_ENCODER_MODEL = config["cross_encoder_model_name"]

