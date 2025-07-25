from typing import List, Optional
from pydantic import BaseModel, Field

class Heading(BaseModel):
    """Represents a single hierarchical heading found in the document."""
    # Changed level to a string to support "H1", "H2", etc.
    level: str = Field(..., description="The hierarchy level of the heading (e.g., 'H1', 'H2').")
    text: str = Field(..., description="The clean text of the heading.")
    page: int = Field(..., description="The page number where the heading is found (1-based).")

class DocumentStructure(BaseModel):
    """The final structured output for a single processed PDF."""
    title: Optional[str] = Field(None, description="The main title of the document.")
    outline: List[Heading] = Field(default_factory=list, description="A hierarchical list of all detected headings.")

