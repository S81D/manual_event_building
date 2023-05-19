import os, sys

run_number = sys.argv[1]

raw_data_dir = "/pnfs/annie/persistent/raw/raw/" + run_number + "/"
processed_dir = "/pnfs/annie/persistent/processed/processed_hits/R" + run_number + "/"

# Get the list of raw files
raw_files = [file for file in os.listdir(raw_data_dir) if file.startswith("RAWDataR" + run_number)]

# Get the list of processed files
processed_files = [file for file in os.listdir(processed_dir) if file.startswith("ProcessedRawData_TankAndMRDAndCTC_R" + run_number) and not file.endswith(".data")]

# Count the number of raw files
num_raw_files = len(raw_files)

# Calculate the average, minimum, and maximum file sizes of raw files in MB
file_sizes = [os.path.getsize(os.path.join(raw_data_dir, file)) for file in raw_files]
average_size = sum(file_sizes) / len(file_sizes) / (1024 * 1024)  # Convert to MB
min_size = min(file_sizes) / (1024 * 1024)  # Convert to MB
max_size = max(file_sizes) / (1024 * 1024)  # Convert to MB

# Count the number of processed files
num_processed_files = len(processed_files)

# Find the missing processed files
missing_files = []
for file in raw_files:
    expected_processed_file = "ProcessedRawData_TankAndMRDAndCTC_R" + file[8:]  # Remove "RAWDataR" prefix
    if expected_processed_file not in processed_files:
        missing_files.append(expected_processed_file)

# Print the results
print("\nNumber of raw files: ", num_raw_files)
print("Average file size (MB): ", round(average_size))
print("Minimum file size (MB): ", round(min_size))
print("Maximum file size (MB): ", round(max_size))
print("Number of processed files: ", num_processed_files)
print("Missing processed files: ", missing_files)
print('\n')
