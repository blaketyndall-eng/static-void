from sqlalchemy import Text, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class AppBlueprintORM(Base):
    __tablename__ = "app_blueprints"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    app_type: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    target_users: Mapped[list[str]] = mapped_column(JSON, default=list)
    workflows: Mapped[list[str]] = mapped_column(JSON, default=list)
    required_engines: Mapped[list[str]] = mapped_column(JSON, default=list)
    primary_views: Mapped[list[str]] = mapped_column(JSON, default=list)
    data_sources: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")


class AppScaffoldPlanORM(Base):
    __tablename__ = "app_scaffold_plans"

    blueprint_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    steps: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_frameworks: Mapped[list[str]] = mapped_column(JSON, default=list)
    generated_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    tech_debt_items: Mapped[list[str]] = mapped_column(JSON, default=list)
