import re

input_string = "MS0044 MS0044 Series 41 Series 41 Box 1 Box 1 Folder 1 Folder 1 item 1 item 1"

words = input_string.split()
unique_words = []
folder_number = None
item_number = None

for word in words:
    if word.startswith('Folder'):
        folder_number = re.search(r'\d+', word).group()
        unique_words.append(word)
    elif word.startswith('item'):
        item_number = re.search(r'\d+', word).group()
        unique_words.append(word)
    else:
        if word not in unique_words:
            unique_words.append(word)

output_string = ' '.join(unique_words)
print(output_string)