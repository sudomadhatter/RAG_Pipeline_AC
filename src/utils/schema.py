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
    'AC 91-73B', 'AC 91-74B', 'AC 120-12A', 'AC 120-71B', 'AC 120-80', 
    'AC 120-111',
    # Other
    'FAA-S-ACS-6C', 'FAA Safety Briefing "Startle Response"'
}

class ContentSource(BaseModel):
    mimeType: str
    uri: str

class CurriculumStructData(BaseModel):
    acs_code: str
    title: str
    type: str
    ancestral_context: str
    reg_keys: List[str]
    doc_keys: List[str] = Field(..., min_length=1)
    keywords: List[str]

    @field_validator('reg_keys', 'doc_keys', mode='before')
    def clean_na_and_strip(cls, v):
        if not v:
            return []
        cleaned = []
        for x in v:
            val = x.strip()
            if val.upper() != 'N/A' and val:
                cleaned.append(val)
        return cleaned

    @field_validator('doc_keys')
    def validate_doc_keys(cls, v: List[str]) -> List[str]:
        # Enforce that every doc_key is document-level AND in DB2_VOCABULARY
        for key in v:
            if '(' in key or 'Ch ' in key or 'Chapter' in key:
                raise ValueError(f"Chapter-level key detected: '{key}'. Must be document-level only.")
            if key not in DB2_VOCABULARY:
                raise ValueError(f"doc_key '{key}' is NOT in DB2_VOCABULARY. Must be a valid DB2 tag.")
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
