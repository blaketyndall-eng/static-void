from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ImageStudioWorkspaceORM(Base):
    __tablename__ = 'image_studio_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    creative_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ImageStudioSnapshotORM(Base):
    __tablename__ = 'image_studio_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    model_registry: Mapped[list[str]] = mapped_column(JSON, default=list)
    generation_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    prompt_recipes: Mapped[list[str]] = mapped_column(JSON, default=list)
    control_profiles: Mapped[list[str]] = mapped_column(JSON, default=list)
    edit_profiles: Mapped[list[str]] = mapped_column(JSON, default=list)
    artifact_paths: Mapped[list[str]] = mapped_column(JSON, default=list)
    variant_scoring_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    creative_reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    deployment_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)


class ImageStudioRenderJobORM(Base):
    __tablename__ = 'image_studio_render_jobs'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(40), index=True)
    mode: Mapped[str] = mapped_column(String(80), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    negative_prompt: Mapped[str] = mapped_column(Text, default='')
    model_name: Mapped[str] = mapped_column(String(255), default='')
    width: Mapped[int] = mapped_column(default=1024)
    height: Mapped[int] = mapped_column(default=1024)
    steps: Mapped[int] = mapped_column(default=20)
    guidance_scale: Mapped[float] = mapped_column(Float, default=7.5)
    seed: Mapped[int | None] = mapped_column(nullable=True)
    control_type: Mapped[str] = mapped_column(String(80), default='')
    source_asset_path: Mapped[str] = mapped_column(Text, default='')
    mask_asset_path: Mapped[str] = mapped_column(Text, default='')
    output_asset_path: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True, default='queued')
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
