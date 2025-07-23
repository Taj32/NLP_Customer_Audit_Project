import pyarrow as pa
import os
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import logging
import psutil

logging.basicConfig(filename="script_progress.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def load_arrow_files_with_pyarrow(data_dir):
    print(f"Loading .arrow files from '{data_dir}'...")
    arrow_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".arrow")]
    print(f"Found {len(arrow_files)} .arrow files.")
    if not arrow_files:
        raise FileNotFoundError(f"No .arrow files found in {data_dir}")

    tables = []
    for file in arrow_files:
        print(f"Reading .arrow file: {file}")
        with open(file, "rb") as f:
            reader = pa.RecordBatchStreamReader(f)
            table = reader.read_all()
            print(f"Loaded table with {table.num_rows} rows.")  # Print metadata, not raw data
            tables.append(table)

    combined_table = pa.concat_tables(tables)
    print(f"Loaded dataset with {combined_table.num_rows} rows.")
    return combined_table

# Debugging in extract_audio_and_rttm_with_pyarrow
def extract_audio_and_rttm_with_pyarrow(table, rttm_dir):
    print("Extracting audio file paths and matching with RTTM files...")
    audio_files = table["audio"].to_pylist()
    print(f"Found {len(audio_files)} audio entries in the dataset.")

    # Debugging: Inspect the first few entries
    print("Inspecting the first few audio entries...")
    for i, audio_file in enumerate(audio_files[:5]):
        #print(f"Entry {i + 1}: {repr(audio_file)}")
        if isinstance(audio_file, dict):
            for key, value in audio_file.items():
                print("hi")
                print(f"{key}")
        break
    
    if len(audio_files) > 0:
        first_audio_file = audio_files[0]
        if isinstance(first_audio_file, dict):
            # Decode byte string keys into regular strings
            first_audio_file = {
                (key.decode('utf-8') if isinstance(key, bytes) else key): value
                for key, value in first_audio_file.items()
            }
            print(f"First audio file: {first_audio_file}")
            path = first_audio_file.get('path')
            if path is None:
                print("Path of the first audio file is None. Skipping this entry.")
            else:
                print(f"Path of the first audio file: {path}")
        else:
            print(f"First audio file is not a dictionary: {repr(first_audio_file)}")
    else:
        print("audio_files is empty.")
    
    return
    

    audio_rttm_pairs = []
    for i, audio_file in enumerate(audio_files):
        print(f"Processing audio file {i + 1}/{len(audio_files)}...")

        # Check if audio_file is a dictionary
        if not isinstance(audio_file, dict):
            print(f"Warning: Skipping invalid audio entry (not a dict): {repr(audio_file)}")
            continue

        # Check if "path" exists and is valid
        if "path" not in audio_file or not audio_file["path"]:
            print(f"Warning: Skipping invalid audio entry (missing 'path'):") #{repr(audio_file)}")
            continue

        # Construct RTTM file path
        rttm_file = os.path.join(rttm_dir, os.path.splitext(os.path.basename(audio_file["path"]))[0] + ".rttm")
        if os.path.exists(rttm_file):
            print(f"Matched audio file with RTTM: {audio_file['path']} -> {rttm_file}")
            audio_rttm_pairs.append((audio_file["path"], rttm_file))
        else:
            print(f"Warning: No RTTM file found for {audio_file['path']}")

    print(f"Total matched audio-RTTM pairs: {len(audio_rttm_pairs)}")
    return audio_rttm_pairs

# Debugging in split_dataset
def split_dataset(audio_rttm_pairs, output_dir, train_ratio=0.7, dev_ratio=0.2):
    print("Splitting dataset into train, dev, and test subsets...")
    print(f"Total pairs to split: {len(audio_rttm_pairs)}")

    train_files, temp_files = train_test_split(audio_rttm_pairs, train_size=train_ratio, random_state=42)
    dev_files, test_files = train_test_split(temp_files, train_size=dev_ratio / (1 - train_ratio), random_state=42)

    print(f"Train: {len(train_files)}, Dev: {len(dev_files)}, Test: {len(test_files)}")

    def copy_files(file_list, subset):
        print(f"Copying files to {subset} subset...")
        audio_subset_dir = os.path.join(output_dir, subset, "audio")
        rttm_subset_dir = os.path.join(output_dir, subset, "annotations")
        os.makedirs(audio_subset_dir, exist_ok=True)
        os.makedirs(rttm_subset_dir, exist_ok=True)

        for audio_file, rttm_file in tqdm(file_list, desc=f"Copying files to {subset} subset"):
            print(f"Copying {audio_file} and {rttm_file} to {subset} subset.")
            shutil.copy(audio_file, os.path.join(audio_subset_dir, os.path.basename(audio_file)))
            shutil.copy(rttm_file, os.path.join(rttm_subset_dir, os.path.basename(rttm_file)))

    copy_files(train_files, "train")
    copy_files(dev_files, "dev")
    copy_files(test_files, "test")

    print("Dataset split completed!")
    print(f"Train: {len(train_files)} files")
    print(f"Dev: {len(dev_files)} files")
    print(f"Test: {len(test_files)} files")

# Define paths
data_dir = "D:/Python Projects/NLP_Customer_Audit_Project/data/huggingface_dataset/talkbank___callhome/eng/0.0.0/17c8a153215aa7c50b805078fd6284ba81c2fc47"
rttm_dir = "D:/Python Projects/NLP_Customer_Audit_Project/data/rttm_files"
output_dir = "D:/Python Projects/NLP_Customer_Audit_Project/data/split_dataset"

# Load the dataset
try:
    table = load_arrow_files_with_pyarrow(data_dir)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# Extract audio and RTTM file paths
audio_rttm_pairs = extract_audio_and_rttm_with_pyarrow(table, rttm_dir)

print("temp stop..")


# Split the dataset
#split_dataset(audio_rttm_pairs, output_dir)