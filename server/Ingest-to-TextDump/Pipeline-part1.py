import pdfplumber
import json


textDump = ""


def extract_text_from_page(page):
   """
   Extracts text from a single PDF page, attempting OCR if the initial extraction fails.
   """
   text = page.extract_text(x_tolerance=3, y_tolerance=3)
   if not text:
       text = page.extract_text(x_tolerance=3, y_tolerance=3, use_text_flow=True, extra_attrs=["fontname", "size"])
   return text




# Specify the path to your PDF textbook
pdf_path = "/Users/jq4386/Github/Personal/berkeley-hackathon/Chapter 9.pdf"


# Text Extraction Process
extracted_text = ""
with pdfplumber.open(pdf_path) as pdf:
   for page_num, page in enumerate(pdf.pages):
       print(f"Processing page {page_num + 1}...")
       extracted_text += extract_text_from_page(page) + "\n\n"


# Save the extracted text to a file
with open("extracted_text.txt", "w", encoding="utf-8") as f:
   f.write(extracted_text)


print("Text extraction complete! The extracted text has been saved to extracted_text.txt.")


# Append the extracted text to the textDump
textDump += extracted_text




# # Store the textDump as a JSON file (optional)
# Create the JSON structure
data = {
   "project_name": "Preferential Trade Agreements",
   "chapter": "9",
   "type": "TextDump",
   "content": textDump
}


print(data)





