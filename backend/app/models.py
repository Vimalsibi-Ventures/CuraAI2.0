# backend/app/models.py

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal


# -----------------------------
# User Authentication Models
# -----------------------------

class UserSignup(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    role: Literal['Patient', 'Professional'] = Field(..., description="User role type")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    token: str = Field(..., description="JWT authentication token")
    user_id: str = Field(..., description="Unique identifier of the user")
    role: str = Field(..., description="User role (Patient or Professional)")


# -----------------------------
# Chat Models
# -----------------------------

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant'] = Field(..., description="Message author (user or assistant)")
    content: str = Field(..., description="Text content of the message")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's input message")
    history: List[ChatMessage] = Field(..., description="Conversation history")
    session_id: Optional[str] = Field(None, description="Optional session ID")


class SourceNode(BaseModel):
    name: str = Field(..., description="Title or identifier of the source document")
    url: str = Field(..., description="URL of the source document if available")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI-generated response text")
    sources: List[SourceNode] = Field(..., description="List of referenced source documents")
    type: Literal['RAG', 'SYMPTOM'] = Field(..., description="Response type")
    session_id: str = Field(..., description="Ongoing chat session ID")


# -----------------------------
# Report Models
# -----------------------------

class ReportRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for which report is requested")


class ReportResponse(BaseModel):
    summary: str = Field(..., description="Summarized report text")
    triage: str = Field(..., description="Triage analysis or classification")
    prep: str = Field(..., description="Preparation or next-step guidance")


# -----------------------------
# RAG (Retrieval-Augmented Generation) Models
# -----------------------------

class RAGRequest(BaseModel):
    user_question: str = Field(..., description="User's question for RAG engine")


class RAGResponse(BaseModel):
    answer: str = Field(..., description="RAG engine's generated answer")
    sources: List[SourceNode] = Field(..., description="List of cited sources")
