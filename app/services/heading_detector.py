import fitz  # PyMuPDF
import re
from collections import Counter
from typing import List, Dict, Any, Optional

from app.models.documents import DocumentStructure, Heading

# --- Configuration for Heuristics ---
# These values can be tuned for better performance
BODY_SIZE_THRESHOLD_RATIO = 1.15 # Lowered threshold to catch more potential headings
H1_THRESHOLD_RATIO = 1.6
H2_THRESHOLD_RATIO = 1.3

# Regular expression to detect numeric prefixes like "1.", "2.1", "3.1.4"
NUMERIC_PREFIX_RE = re.compile(r'^\s*(\d+(\.\d+)*)\s+')

class HeadingDetector:
    """
    Analyzes a PDF to extract its title and hierarchical headings (H1, H2, H3).
    This version includes more advanced heuristics for structural analysis.
    """

    def __init__(self, pdf_bytes: bytes):
        self.doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self._all_spans = self._get_all_spans()
        self.body_size = self._calculate_body_size()
        self.title = self._find_title()

    def _get_all_spans(self) -> List[Dict[str, Any]]:
        """Extract all text spans from all pages with page numbers."""
        all_spans = []
        for page_num, page in enumerate(self.doc, 1):
            # Using 'blocks' gives better structural separation than 'spans' alone
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        # Clean up line text
                        line_text = "".join(s["text"] for s in line["spans"]).strip()
                        if not line_text:
                            continue
                        
                        # Store line-level information
                        line_info = {
                            "text": line_text,
                            "spans": line["spans"],
                            "bbox": line["bbox"],
                            "page_num": page_num
                        }
                        all_spans.append(line_info)
        return all_spans

    def _calculate_body_size(self) -> float:
        """Calculates the most common font size to use as a proxy for the body text size."""
        if not self._all_spans:
            return 12.0

        # Consider only the font sizes of the first span of each line
        sizes = [round(line["spans"][0]["size"]) for line in self._all_spans if line["spans"]]
        if not sizes:
            return 12.0

        return Counter(sizes).most_common(1)[0][0]

    def _find_title(self) -> Optional[str]:
        """
        Finds the document title by concatenating all text on the first page
        that has the largest font size.
        """
        max_size = 0
        # Search only the first page for the title
        lines_on_first_page = [line for line in self._all_spans if line["page_num"] == 1 and line["spans"]]

        if not lines_on_first_page:
            return None

        # Find the maximum font size on the first page
        for line in lines_on_first_page:
            size = line["spans"][0]["size"]
            if size > max_size:
                max_size = size
        
        # Collect all lines with that max font size
        title_parts = [
            line["text"] for line in lines_on_first_page
            if abs(line["spans"][0]["size"] - max_size) < 0.1 # Use a small tolerance
        ]
        
        title = " ".join(title_parts).strip()
        
        # A simple sanity check for the title
        if title and len(title.split()) < 20:
             return title
        return None

    def _get_heading_level(self, line: Dict[str, Any]) -> Optional[str]:
        """
        Determines the heading level (H1, H2, H3) using a combination of
        numeric prefixes and font styles. Returns None if not a heading.
        """
        text = line["text"]
        first_span = line["spans"][0]
        size = first_span["size"]
        is_bold = "bold" in first_span["font"].lower() or (first_span["flags"] & 2**4)

        # --- Rule 1: Structural Analysis (High Priority) ---
        match = NUMERIC_PREFIX_RE.match(text)
        if match:
            prefix = match.group(1)
            # Count the dots to determine hierarchy level
            level = prefix.count('.') + 1
            if level == 1: return "H1"
            if level == 2: return "H2"
            if level >= 3: return "H3"

        # --- Rule 2: Stylistic Analysis (Fallback) ---
        # Must be bold or significantly larger than body text
        is_stylistically_significant = is_bold or size > (self.body_size * BODY_SIZE_THRESHOLD_RATIO)
        is_short = len(text.split()) < 12 # Headings are usually short
        
        # Avoid classifying headers/footers
        is_likely_content = line["bbox"][1] > 50 and line["bbox"][3] < 750

        if is_stylistically_significant and is_short and is_likely_content:
            rel_size = size / self.body_size
            if rel_size > H1_THRESHOLD_RATIO: return "H1"
            if rel_size > H2_THRESHOLD_RATIO: return "H2"
            # If it's just bold but not much larger, classify as H3
            if is_bold: return "H3"

        return None

    def extract_structure(self) -> DocumentStructure:
        """
        Orchestrates the heading extraction process and returns the final structure.
        """
        outline = []
        processed_lines = set()

        for line in self._all_spans:
            line_text = line["text"]
            line_bbox_tuple = tuple(line['bbox'])
            page_num = line["page_num"]

            # Avoid reprocessing the same line or the title
            if not line_text or line_bbox_tuple in processed_lines or line_text == self.title:
                continue

            level = self._get_heading_level(line)
            if level:
                outline.append(
                    Heading(level=level, text=line_text, page=page_num)
                )
                processed_lines.add(line_bbox_tuple)

        return DocumentStructure(title=self.title, outline=outline)

def process_pdf_for_headings(pdf_bytes: bytes) -> DocumentStructure:
    """High-level function to process a PDF and return its structure."""
    detector = HeadingDetector(pdf_bytes)
    return detector.extract_structure()
