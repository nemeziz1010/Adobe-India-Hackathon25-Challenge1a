import os
import json
from pathlib import Path
import time
from app.services.heading_detector import process_pdf_for_headings

def run_batch_processing():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in /app/input")
        return
    print(f"Found {len(pdf_files)} PDF(s) to process.")
    for pdf_path in pdf_files:
        start_time = time.time()
        print(f"Processing {pdf_path.name}...")
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            document_structure = process_pdf_for_headings(pdf_bytes)
            result_json_dict = document_structure.model_dump(exclude_none=True)
            output_filename = output_dir / f"{pdf_path.stem}.json"
            with open(output_filename, "w", encoding='utf-8') as f:
                json.dump(result_json_dict, f, indent=4, ensure_ascii=False)
            duration = time.time() - start_time
            print(f"Successfully generated {output_filename.name} in {duration:.2f} seconds.")
        except Exception as e:
            print(f"ERROR: Failed to process {pdf_path.name}: {e}")

if __name__ == "__main__":
    print("--- Starting PDF Structure Extraction (Challenge 1A) ---")
    total_start_time = time.time()
    run_batch_processing()
    total_duration = time.time() - total_start_time
    print(f"--- Batch processing complete in {total_duration:.2f} seconds. ---")