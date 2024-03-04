import fitz  # PyMuPDF
import os
import hashlib
import json
import sys
import logging

def setup_logging():
    """ Set up logging to a file in the script's directory. """
    logging.basicConfig(filename='process_pdfs.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

def generate_md5(filename):
    """ Generate MD5 hash of a file. """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_hash_file(hash_file):
    """ Read MD5 hashes from a file. """
    try:
        with open(hash_file, 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def write_hash_file(hash_file, hash_value):
    """ Write a new MD5 hash to the file. """
    with open(hash_file, 'a') as file:
        file.write(hash_value + "\n")

def write_to_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def extract_text_with_fonts(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        detailed_text_info = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                block_type = b["type"]
                for line in b.get("lines", []):
                    line_text = ""
                    line_details = []
                    for span in line["spans"]:
                        span_text = span['text']
                        font_name = span['font']
                        font_size = span['size']
                        is_bold = "Bold" in font_name
                        is_italic = "Italic" in font_name
                        color = span['color']
                        position = span['bbox']

                        line_text += span_text
                        line_details.append({
                            'text': span_text,
                            'font_name': font_name,
                            'font_size': font_size,
                            'is_bold': is_bold,
                            'is_italic': is_italic,
                            'color': color,
                            'position': position
                        })

                    detailed_text_info.append({
                        'page_number': page_num + 1,
                        'block_type': block_type,
                        'line_text': line_text,
                        'line_details': line_details
                    })
        doc.close()
        return detailed_text_info
    except Exception as e:
        logging.error(f"Error processing file {pdf_path}: {e}")
        return []


def assign_font_rankings(font_details, precision=2, max_font_size=28):
    # Round font sizes to the specified precision and filter out fonts larger than max_font_size
    filtered_fonts = [
        {**font, 'font_size': round(font['font_size'], precision)}
        for font in font_details
        if font['font_size'] <= max_font_size
    ]

    # Sort by font size, larger sizes first
    sorted_fonts = sorted(filtered_fonts, key=lambda x: x['font_size'], reverse=True)
    
    # Assign rankings and count occurrences
    current_rank = 0
    last_size = None
    font_rankings = []

    for font in sorted_fonts:
        if font['font_size'] != last_size:
            current_rank += 1
            last_size = font['font_size']
        font_rankings.append({**font, 'rank': current_rank})

    return font_rankings


def convert_to_markdown(json_data, font_rankings, min_font_size=9, h1_ranks=[1, 2, 3], h2_ranks=[4, 5 ], h3_ranks=[6, 7, 8], h4_ranks=[9, 10]):
    markdown_content = ""
    font_rank_mapping = {(round(font['font_size'], 2), font['is_bold']): font['rank'] for font in font_rankings}
    current_heading_level = None

    for item in json_data:
        for line_detail in item["line_details"]:
            font_key = (round(line_detail["font_size"], 2), line_detail["is_bold"])  # Match rounding precision
            rank = font_rank_mapping.get(font_key)
            line_text = line_detail["text"].strip()

            if rank and line_detail["font_size"] >= min_font_size:
                # Determine heading level based on rank
                if rank in h1_ranks:
                    heading_level = 1
                elif rank in h2_ranks:
                    heading_level = 2
                elif rank in h3_ranks:
                    heading_level = 3
                elif rank in h4_ranks:
                    heading_level = 4
                else:
                    heading_level = None

                if heading_level:
                    if heading_level == current_heading_level:
                        # Merge with the previous line
                        markdown_content += f" {line_text}"
                    else:
                        # Start a new line
                        markdown_content += f"\n\n{'#' * heading_level} {line_text}\n\n"
                        current_heading_level = heading_level
                else:
                    # Normal text
                    markdown_content += f"{line_text} "
                    current_heading_level = None
            else:
                pass
                print(f"Ignoring text: '{line_detail['text']}' due to small font size: {line_detail['font_size']} (Key: {font_key})")

    return markdown_content.strip()


def process_json_to_markdown(json_file_path):
    # Generate Markdown file path by replacing .json extension with .md
    markdown_file_path = json_file_path.rsplit('.', 1)[0] + '.md'

    # Load JSON data from file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    # Extract unique font details and count occurrences
    font_details = {}
    for item in json_data:
        for line_detail in item["line_details"]:
            font_key = (line_detail["font_name"], line_detail["font_size"], line_detail["is_bold"])
            if font_key in font_details:
                font_details[font_key]['count'] += 1
            else:
                font_details[font_key] = {'font_name': line_detail["font_name"], 'font_size': line_detail["font_size"], 'is_bold': line_detail["is_bold"], 'count': 1}

    # Convert to list and assign rankings
    font_rankings = assign_font_rankings(list(font_details.values()))

    # Convert JSON data to Markdown
    markdown = convert_to_markdown(json_data, font_rankings)

    # Write Markdown to file
    with open(markdown_file_path, 'w') as md_file:
        md_file.write(markdown)
    print(f"Markdown content created and saved to {markdown_file_path}")

def process_pdfs_in_directory(pdf_directory):
    processed_folder = os.path.join(pdf_directory, "processed_pdf_to_jsons")
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    hash_file = "processed_hashes.log"
    processed_hashes = read_hash_file(hash_file)

    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            try:
                pdf_path = os.path.join(pdf_directory, filename)
                file_hash = generate_md5(pdf_path)

                if file_hash in processed_hashes:
                    logging.info(f"File {filename} already processed. Skipping...")
                    continue

                detailed_text_info = extract_text_with_fonts(pdf_path)
                json_filename = f"{filename.replace('.pdf', '')}_{file_hash}.json"
                json_path = os.path.join(processed_folder, json_filename)
                write_to_json_file(detailed_text_info, json_path)
                process_json_to_markdown(json_path)
                write_hash_file(hash_file, file_hash)
            except Exception as e:
                logging.error(f"Error processing PDF {filename}: {e}")

if __name__ == "__main__":
    setup_logging()
    if len(sys.argv) > 1:
        pdf_directory = sys.argv[1]
    else:
        pdf_directory = "workspace/docs"  # Default directory
    process_pdfs_in_directory(pdf_directory)