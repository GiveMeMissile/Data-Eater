import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# File Constants:
DATA = "Datasets"  # Data Saving Folder Name
PARQUET = DATA + "/" + "Parquet"
CSV = DATA + "/" + "CSV"
SQLITE = DATA + "/" + "SQLite"
JSONL = DATA + "/" + "JSONL"

# GUI Options Constants from Config:
NUM_SAMPLE_STEPS = config["gui"]["steps_for_sample_size"]
MIN_SAMPLE = config["gui"]["min_sample"]
DEFAULT_SAMPLE = config["gui"]["default_sample"]
MIN_BI = config["gui"]["min_bi_encoding"]
MAX_BI = config["gui"]["max_bi_encoding"]
DEFAULT_BI = config["gui"]["default_bi_encoding"]
MAX_INPUT = config["gui"]["max_input_box"]
MIN_INPUT = config["gui"]["min_input_box"]
DEFAULT_INPUT = config["gui"]["default_input_box"]
MIN_OVERFLOW = config["gui"]["overflow_min"]
MAX_OVERFLOW = config["gui"]["overflow_max"]
DEFAULT_OVERFLOW = config["gui"]["default_overflow"]

# GUI Tags:

# Option Tags: 
OPTION_WINDOW_TAG = "select"
FILTER_SELECT_TAG = "filter"
FILTER_OPTION_1 = "Word"
FILTER_OPTION_2 = "Sample"
FILTER_TEXT_TAG = "input_text"
SAMPLE_TAG = "sample_num"
SAMPLE_TEXT_TAG = "sample_num_text"
FILE_TEXT_TAG = "file_text"
FILE_SELECT_TAG = "file"
SIMILARITY_TEXT_TAG = "similarity_text"
SIMILARITY_SELECT_TAG = "similarity"
OVERFLOW_SELECT_TAG = "overflow"
SUBMIT_TAG = "submit"
FAILED_TAG = "fail_text"

# Display Tags:
DISPLAY_WINDOW_TAG = "display"

# AI Model Options:
BI_ENCODER_MODEL = config["bi_encoder_model_name"]
CROSS_ENCODER_MODEL = config["cross_encoder_model_name"]
BACKUP_BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BACKUP_CROSS_ENCODER_MODEL = "cross-encoder/stsb-roberta-base"

BROWSER = config["scraper"]["browser"]
HEADLESS = config["scraper"]["headless"]
BATCH_SIZE = config["scraper"]["data_batch_size"]