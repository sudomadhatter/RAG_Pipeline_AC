from pydantic import BaseModel, Field, field_validator
from typing import List

class ContentSource(BaseModel):
    mimeType: str
    uri: str

class CurriculumStructData(BaseModel):
    acs_code: str
    title: str
    type: str = "lesson_chunk"
    ancestral_context: str
    reg_keys: List[str] = Field(default_factory=list)
    doc_keys: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

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
