import os, sys

run_number = sys.argv[1]

raw_data_dir = "/pnfs/annie/persistent/raw/raw/" + run_number + "/"
#processed_dir = "/pnfs/annie/persistent/processed/processed_hits_new_charge/R" + run_number + "/"
processed_dir = "/pnfs/annie/scratch/users/doran/output/" + run_number + "/"

# Get the list of raw files
raw_files = [file for file in os.listdir(raw_data_dir) if file.startswith("RAWDataR" + run_number)]

# Get the list of processed files
processed_files = [file for file in os.listdir(processed_dir) if file.startswith("ProcessedRawData_TankAndMRDAndCTC_R" + run_number) and not file.endswith(".data")]

# Count the number of raw files
num_raw_files = len(raw_files)

# Count the number of processed files
num_processed_files = len(processed_files)

# Find the missing processed files
missing_files = []
for file in raw_files:
    expected_processed_file = "ProcessedRawData_TankAndMRDAndCTC_R" + file[8:]  # Remove "RAWDataR" prefix
    if expected_processed_file not in processed_files:
        missing_files.append(int(expected_processed_file[42:]))

# Print the results
print("\nNumber of raw files: ", num_raw_files)
print("Number of processed files: ", num_processed_files)
print("Number of missing files: ", num_raw_files-num_processed_files)
print("Missing processed files: ", missing_files)
print("\nPercentage processed: ", round((num_processed_files/num_raw_files)*100,2), '%')
print('\n')
