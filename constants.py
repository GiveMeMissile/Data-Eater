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
DEFAULT_WORD_TEXT = config["gui"]["default_word_input"]
MIN_WEBSITES = config["gui"]["min_websites"]
MAX_WEBSITES = config["gui"]["max_websites"]
DEFAULT_WEBSITES = config["gui"]["num_default_websites"]
DEFAULT_WEBSITE_1 = config["gui"]["default_websites"][0]
DEFAULT_WEBSITE_2 = config["gui"]["default_websites"][1]
DEFAULT_WEBSITE_3 = config["gui"]["default_websites"][2]

# GUI Tags:

# Option Tags: 
OPTION_WINDOW_TAG = "select"
FILTER_SELECT_TAG = "filter"
SAMPLE_FILTER = "Sample"
FILTER_TEXT_TAG = "input_text"
WORD_FILTER = "word_filter"
WORD_FILTER_TEXT = "word_filter_text"
SAMPLE_TAG = "sample_num"
SAMPLE_TEXT_TAG = "sample_num_text"
FILE_TEXT_TAG = "file_text"
FILE_SELECT_TAG = "file"
SIMILARITY_TEXT_TAG = "similarity_text"
SIMILARITY_SELECT_TAG = "similarity"
OVERFLOW_SELECT_TAG = "overflow"
SUBMIT_TAG = "submit"
SUBMIT_TEXT_TAG = "submit_text"
FAILED_TAG = "fail_text"
NUM_WEBSITE_TAG = "number_websites"
WEBSITE_INPUT_TAG = "websites"
FILE_NAME_TAG = "file_name"

# Display Tags:
DISPLAY_WINDOW_TAG = "display"

# AI Model Options:
BI_ENCODER_MODEL = config["bi_encoder_model_name"]
CROSS_ENCODER_MODEL = config["cross_encoder_model_name"]
BACKUP_BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BACKUP_CROSS_ENCODER_MODEL = "cross-encoder/stsb-roberta-base"

# Scraper
BROWSER = config["scraper"]["browser"]
HEADLESS = config["scraper"]["headless"]
BATCH_SIZE = config["scraper"]["data_batch_size"]
REQUEST_LIMIT = config["scraper"]["request_limit"]

NUM_MOUSE_SCROLLS = 5
JUDGE_REJECT_SCORE = 0
JUDGE_SCORE_CHANGE = 1
TEXT_LOSS_THRESHOLD = 0.25
LIMIT_WINDOW = 60