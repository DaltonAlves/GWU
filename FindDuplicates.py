import os
import hashlib
import json

def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def find_duplicates(directory):
    files_and_hashes = {}
    duplicate_files = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            sha1_hash = calculate_sha1(file_path)
            relative_path = os.path.relpath(file_path, directory)  # Get relative path

            # Check if the hash is already in the dictionary
            if sha1_hash in files_and_hashes:
                # This is a duplicate file
                original_relative_path = files_and_hashes[sha1_hash]
                duplicate_files.setdefault(sha1_hash, []).append(original_relative_path)
                duplicate_files[sha1_hash].append(relative_path)
            else:
                # Add the hash and relative path to the dictionary
                files_and_hashes[sha1_hash] = relative_path

    # Filter out non-duplicates
    duplicate_files = {k: v for k, v in duplicate_files.items() if len(v) > 1}

    # Save the information to a JSON file in the same directory
    output_data = {
        "files_and_hashes": files_and_hashes,
        "duplicate_files": duplicate_files
    }

    output_file_path = os.path.join(directory, 'duplicate_files.json')
    with open(output_file_path, 'w') as output_file:
        json.dump(output_data, output_file, indent=4)


# Input the directory you'd like to check for duplicate files
directory_path = r'C:\Users\dalton_alves\Desktop\test'
find_duplicates(directory_path)