import csv
import os

# Define paths
base_dir = r"E:\Mypython\土地家屋調査士試験"
input_file = os.path.join(base_dir, "ai解答.csv")
output_dir = os.path.join(base_dir, "app")
output_file = os.path.join(output_dir, "data.csv")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define headers
headers = [
    "Year",
    "QuestionID",
    "Category",
    "Topic",
    "Question",
    "Answer",
    "Explanation_NotebookLM",
    "Explanation_Gemini"
]

print(f"Reading from: {input_file}")
print(f"Writing to: {output_file}")

try:
    with open(input_file, 'r', encoding='utf-8-sig', newline='') as infile:
        reader = csv.reader(infile)
        data = list(reader)

    cleaned_data = []
    replacement_count = 0
    
    for row in data:
        cleaned_row = []
        for cell in row:
            if "たかゆきさん" in cell:
                cell = cell.replace("たかゆきさん", "")
                replacement_count += 1
            cleaned_row.append(cell)
        cleaned_data.append(cleaned_row)

    print(f"Removed 'たかゆきさん' from {replacement_count} cells.")

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        writer.writerows(cleaned_data)

    print("Successfully created data.csv with headers and cleaned content.")

except Exception as e:
    print(f"Error: {e}")
