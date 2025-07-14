from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import NoteCreate, NoteUpdate, NoteInDB
from .db import db_create_note, db_get_notes, db_update_note, db_delete_note

app = FastAPI(
    title="Personal Notes Backend",
    description="FastAPI backend service for managing personal notes. Provides RESTful CRUD endpoints for note management.",
    version="1.0.0",
    openapi_tags=[
        {"name": "notes", "description": "Operations related to notes management."},
        {"name": "health", "description": "Health check endpoint."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/notes", response_model=List[NoteInDB], summary="Get all notes", tags=["notes"])
def get_notes():
    """
    Returns a list of all personal notes, ordered by creation time (most recent first).
    """
    return db_get_notes()

# PUBLIC_INTERFACE
@app.post("/notes", response_model=NoteInDB, status_code=status.HTTP_201_CREATED, summary="Create a note", tags=["notes"])
def create_note(note: NoteCreate):
    """
    Creates a new note with the given title and content.

    Parameters:
        - note: NoteCreate schema body (title: str, content: str)

    Returns:
        - Created note with id, title, content, created_at, and updated_at fields.
    """
    new_note = db_create_note(note)
    return new_note

# PUBLIC_INTERFACE
@app.put("/notes/{note_id}", response_model=NoteInDB, summary="Update a note", tags=["notes"])
def update_note(note_id: int, note: NoteUpdate):
    """
    Updates an existing note identified by note_id with provided fields.

    Parameters:
        - note_id: int (path)
        - note: NoteUpdate schema body (title/and/or content)

    Returns:
        - The updated note object
    """
    updated = db_update_note(note_id, note)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found")
    return updated

# PUBLIC_INTERFACE
@app.delete("/notes/{note_id}", response_model=dict, summary="Delete a note", tags=["notes"])
def delete_note(note_id: int):
    """
    Deletes a note identified by note_id.

    Parameters:
        - note_id: int (path)

    Returns:
        - JSON object indicating success (e.g., {"deleted": true})
    """
    deleted = db_delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found")
    return {"deleted": True}
