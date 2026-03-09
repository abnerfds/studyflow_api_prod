# Tipos de dados e restrições estruturais para o Postgres
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

# Ferramenta para gerenciar relacionamentos (Eager/Lazy loading)
from sqlalchemy.orm import relationship

from database import Base


class Candidate(Base):
    __tablename__ = "candidates"  # Nome real da tabela no banco

    # index=True cria um índice no banco, deixando as buscas por ID/Email muito mais rápidas
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    exam_focus = Column(String)

    # Relacionamento 1:N. Permite acessar sessões do candidato via `candidato.sessions`
    sessions = relationship("StudySession", back_populates="candidate")


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight = Column(Integer, default=1)

    sessions = relationship("StudySession", back_populates="discipline")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Chaves Estrangeiras (Foreign Keys) para garantir integridade referencial
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))

    studied_minutes = Column(Integer, nullable=False)
    # Pega o timestamp exato do momento do INSERT automaticamente
    session_date = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos N:1. Permite ver de quem é a sessão via `sessao.candidate.name`
    candidate = relationship("Candidate", back_populates="sessions")
    discipline = relationship("Discipline", back_populates="sessions")
