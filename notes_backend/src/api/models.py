from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base schema for a note."""
    title: str = Field(..., min_length=1, max_length=128, description="Title of the note")
    content: str = Field(..., min_length=1, description="Content/body of the note")

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=128, description="Title of the note")
    content: Optional[str] = Field(None, min_length=1, description="Content/body of the note")

# PUBLIC_INTERFACE
class NoteInDB(NoteBase):
    """Schema for a note as stored in the database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
