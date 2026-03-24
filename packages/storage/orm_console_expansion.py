from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ConsoleArmWorkspaceORM(Base):
    __tablename__ = 'console_arm_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    arm_type: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ConsoleArmSnapshotORM(Base):
    __tablename__ = 'console_arm_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    focus_areas: Mapped[list[str]] = mapped_column(JSON, default=list)
    active_tracks: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    maturity_score: Mapped[float] = mapped_column(Float, default=0.0)
