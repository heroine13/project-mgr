"""
Document Version Control Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base


class Document(Base):
    """Document model with version control"""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Category and tags
    category_id = Column(Integer, ForeignKey("document_categories.id"), nullable=True)
    category = Column(String(100))  # Legacy: simple string category
    tags = Column(String(500))  # Comma separated tags
    
    # Project link
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Current version
    current_version = Column(Integer, default=1)
    
    # Access control
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project")
    category_obj = relationship("DocumentCategory", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', version={self.current_version})>"


class DocumentVersion(Base):
    """Document version history"""
    
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Version info
    version_notes = Column(Text)  # Version changelog
    is_initial = Column(Boolean, default=False)  # First version
    
    # Status
    is_current = Column(Boolean, default=False)
    isarchived = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, version={self.version_number})>"


class DocumentComment(Base):
    """Document version comments"""
    
    __tablename__ = "document_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    line_number = Column(Integer)  # For line-specific comments
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document")
    version = relationship("DocumentVersion")
    user = relationship("User")
    
    def __repr__(self):
        return f"<DocumentComment(id={self.id}, document_id={self.document_id})>"