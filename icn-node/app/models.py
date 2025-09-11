from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    urn: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    public_key: Mapped[str] = mapped_column(String(512), nullable=False)
    org_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from_invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="from_org", foreign_keys="Invoice.from_org_id"
    )
    to_invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="to_org", foreign_keys="Invoice.to_org_id"
    )
    attestations_given: Mapped[list["Attestation"]] = relationship(
        back_populates="attestor_org", foreign_keys="Attestation.attestor_org_id"
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    from_org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"), index=True)
    to_org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"), index=True)

    lines: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    terms: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="proposed", index=True)
    status_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    signatures: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    prev_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    row_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from_org: Mapped[Org] = relationship(back_populates="from_invoices", foreign_keys=[from_org_id])
    to_org: Mapped[Org] = relationship(back_populates="to_invoices", foreign_keys=[to_org_id])

    __table_args__ = (
        Index("ix_invoices_from_to", "from_org_id", "to_org_id"),
    )


class Attestation(Base):
    __tablename__ = "attestations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_type: Mapped[str] = mapped_column(String(64), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attestor_org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"), index=True)
    claims: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    signature: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    attestor_org: Mapped[Org] = relationship(back_populates="attestations_given")

    __table_args__ = (
        Index("ix_attestations_subject", "subject_type", "subject_id"),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    row_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    op_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    signature: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    operations_count: Mapped[int] = mapped_column(Integer, nullable=False)
    merkle_root: Mapped[str] = mapped_column(String(128), nullable=False)
    prev_checkpoint_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    signature: Mapped[str] = mapped_column(String(1024), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


