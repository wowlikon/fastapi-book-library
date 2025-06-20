from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict

from ..database import get_session
from ..models import Author, Book, AuthorBookLink

router = APIRouter(prefix="/relationships", tags=["relations"])

# Add author to book
@router.post("/", response_model=AuthorBookLink)
def add_author_to_book(author_id: int, book_id: int, session: Session = Depends(get_session)):
    # Check if author and book exist
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if relationship already exists
    existing_link = session.exec(
        select(AuthorBookLink)
        .where(AuthorBookLink.author_id == author_id)
        .where(AuthorBookLink.book_id == book_id)
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create new relationship
    link = AuthorBookLink(author_id=author_id, book_id=book_id)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

# Remove author from book
@router.delete("/", response_model=Dict[str, str])
def remove_author_from_book(author_id: int, book_id: int, session: Session = Depends(get_session)):
    # Find the relationship
    link = session.exec(
        select(AuthorBookLink)
        .where(AuthorBookLink.author_id == author_id)
        .where(AuthorBookLink.book_id == book_id)
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Relationship not found")

    session.delete(link)
    session.commit()
    return {"message": "Relationship removed successfully"}