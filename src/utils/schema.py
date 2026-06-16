from pydantic import BaseModel, Field, field_validator
from typing import List

import re

# DB2 document_tags vocabulary — the ONLY tokens that will match a filter
DB2_VOCABULARY = {
    # Regulations
    '14 CFR 1', '14 CFR 43', '14 CFR 61', '14 CFR 68',
    '14 CFR 71', '14 CFR 91', '14 CFR 93', '14 CFR 119',
    '14 CFR 135', '49 CFR 830',
    # Handbooks
    'FAA-H-8083-1B', 'FAA-H-8083-2A', 'FAA-H-8083-3C', 'FAA-H-8083-13A',
    'FAA-H-8083-15B', 'FAA-H-8083-25C', 'AIM',
    # Advisory Circulars
    'AC 00-6B', 'AC 00-45H', 'AC 20-43C', 'AC 23-8C', 'AC 39-7D',
    'AC 43-9C', 'AC 43.13-1B', 'AC 43.13-2B', 'AC 60-22', 'AC 61-65H',
    'AC 61-67C', 'AC 61-98D', 'AC 61-107B', 'AC 61-134A', 'AC 61-142',
    'AC 68-1', 'AC 68-1A', 'AC 90-48D', 'AC 90-109A', 'AC 91-67A',
    'AC 91-73B', 'AC 91-74B', 'AC 120-12A', 'AC 120-71B',
}

class ContentSource(BaseModel):
    mimeType: str
    uri: str

class CurriculumStructData(BaseModel):
    acs_code: str
    title: str
    type: str = "lesson_chunk"
    ancestral_context: str
    reg_keys: List[str] = Field(default_factory=list)
    doc_keys: List[str] = Field(min_length=1)
    keywords: List[str] = Field(default_factory=list)

    @field_validator('reg_keys', 'doc_keys', mode='before')
    @classmethod
    def strip_invalid_keys(cls, v: List[str]) -> List[str]:
        """Remove 'N/A', blank strings, and normalize whitespace."""
        if not isinstance(v, list):
            return v
        return [k.strip() for k in v if k.strip() and k.strip().upper() != 'N/A']

    @field_validator('doc_keys')
    @classmethod
    def validate_doc_keys_non_empty(cls, v: List[str]) -> List[str]:
        """doc_keys must have at least 1 entry after cleaning."""
        if not v:
            raise ValueError(
                'doc_keys must contain at least 1 document-level key. '
                'Empty doc_keys breaks the DB1→DB2 verification hop.'
            )
        return v

    @field_validator('doc_keys', 'reg_keys')
    @classmethod
    def warn_chapter_level_keys(cls, v: List[str]) -> List[str]:
        """Log warnings for chapter-level keys (should be document-level)."""
        import warnings
        for key in v:
            if '(' in key or re.search(r'Ch\s+\d', key):
                warnings.warn(
                    f"Chapter-level key detected: '{key}' — should be document-level. "
                    f"Use 'FAA-H-8083-25C' not 'FAA-H-8083-25C (PHAK Ch 6)'.",
                    UserWarning,
                    stacklevel=2,
                )
        return v

class CurriculumLessonSchema(BaseModel):
    """
    Schema for a single curriculum lesson (DB1).
    Reads the standalone .json metadata file.
    Does not include `content` (which is appended when generating the JSONL).
    """
    id: str
    structData: CurriculumStructData

class LibraryStructData(BaseModel):
    category: str  # e.g., 'regulation', 'handbook', 'advisory_circular'
    title: str
    subfolder: str # e.g., 'regulations', 'handbooks'
    filename: str

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {'regulation', 'handbook', 'advisory_circular'}
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}")
        return v

class LibraryMetadataSchema(BaseModel):
    """
    Schema for a single library document (DB2).
    """
    id: str
    structData: LibraryStructData

# Vertex AI Search JSONL output schemas

class VertexCurriculumEntry(BaseModel):
    id: str
    structData: CurriculumStructData
    content: ContentSource

class VertexLibraryEntry(BaseModel):
    id: str
    structData: LibraryStructData
    content: ContentSource
