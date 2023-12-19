import os
import re
import json

def get_unique_filename(root, new_filename):
    base, ext = os.path.splitext(new_filename)
    counter = 1
    while os.path.exists(os.path.join(root, new_filename)):
        new_filename = f"{base}({counter}){ext}"
        counter += 1
    return new_filename

def remove_spaces(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)

            if " " in filename:
                new_filename = re.sub(r' ', '_', filename)
                new_full_path = os.path.join(root, new_filename)

                if full_path != new_full_path:
                    print(f'Old filename: {filename}')
                    print(f'New filename: {new_filename}')

                    new_filename = get_unique_filename(root, new_filename)

                    user_confirmation = input('Do you want to rename this file? (y/n): ').strip().lower()

                    if user_confirmation == 'y':
                        try:
                            os.rename(full_path, os.path.join(root, new_filename))
                            print(f'Renamed: {filename} to {new_filename}')
                        except Exception as e:
                            print(f'Error renaming {filename}: {e}')
                    else:
                        print(f'Skipped: {filename}')

def identify_bad_characters(directory_path):
    bad_characters = []

    for foldername, subfolders, filenames in os.walk(directory_path):
        for filename in filenames:
            if any(ord(char) > 127 for char in filename):
                file_path = os.path.join(foldername, filename)
                bad_characters.append({"file_path": os.path.relpath(file_path, directory_path), "file_name": filename})

    json_file_path = os.path.join(directory_path, "bad_characters.json")

    try:
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(bad_characters, json_file, ensure_ascii=False, indent=2)
        print(f"Bad characters saved to {json_file_path}")
    except Exception as e:
        print(f'Error saving bad characters to JSON: {e}')

if __name__ == "__main__":
    directory_path = r'C:\Users\dalton_alves\Desktop\test'
    remove_spaces(directory_path)
    identify_bad_characters(directory_path)