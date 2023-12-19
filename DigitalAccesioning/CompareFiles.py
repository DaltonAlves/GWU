import os
import hashlib
import json

def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def get_files_and_hashes(directory):
    files_and_hashes = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_and_hashes[file_path] = calculate_sha1(file_path)
    return files_and_hashes

def find_duplicates_and_unique_files(directory1, directory2):
    # Get dictionaries of files and their SHA-1 hashes for each directory
    hashes1 = get_files_and_hashes(directory1)
    hashes2 = get_files_and_hashes(directory2)

    # Find duplicate files by comparing SHA-1 hashes
    duplicates = {file1: {"file2": file2, "hash": hash1} for file1, hash1 in hashes1.items() for file2, hash2 in hashes2.items() if hash1 == hash2}
    #for file1, hash1 in hashes1.items():
    #for file2, hash2 in hashes2.items():
        #if hash1 == hash2:
            #duplicates[file1] = {"file2": file2, "hash": hash1}


    # Find sets of file hashes for each directory
    hashes_set1 = set(hashes1.values())
    hashes_set2 = set(hashes2.values())

    # Find files with unique hashes in each directory
    unique_files1 = [{file: {"hash": hash_value}} for file, hash_value in hashes1.items() if hash_value not in hashes_set2]
    unique_files2 = [{file: {"hash": hash_value}} for file, hash_value in hashes2.items() if hash_value not in hashes_set1]

    return duplicates, unique_files1, unique_files2

if __name__ == "__main__":
    directory1 = r""
    directory2 = r""

    duplicates, unique_files1, unique_files2 = find_duplicates_and_unique_files(directory1, directory2)

    # Save the JSON objects to files in the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(script_directory, "duplicates.json"), 'w') as duplicates_file:
        json.dump(duplicates, duplicates_file, indent=2)

    with open(os.path.join(script_directory, "unique_files1.json"), 'w') as unique_files1_file:
        json.dump(unique_files1, unique_files1_file, indent=2)

    with open(os.path.join(script_directory, "unique_files2.json"), 'w') as unique_files2_file:
        json.dump(unique_files2, unique_files2_file, indent=2)

    print("Results saved as duplicates.json, unique_files1.json, and unique_files2.json in the script's directory.")