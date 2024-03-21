import os

def identify_zero_bit_files(directory):
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Check if the file has zero bits
            if os.path.getsize(file_path) == 0:
                print(f"Zero-bit file found: {file_path}")

# Replace 'your_directory_path' with the path of the directory you want to search
directory_path = r''

identify_zero_bit_files(directory_path)