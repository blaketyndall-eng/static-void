from sqlalchemy.orm import Session

from packages.domain.image_studio import (
    ImageStudioRenderJob,
    ImageStudioSnapshot,
    ImageStudioStatus,
    ImageStudioWorkspace,
)
from packages.storage.orm_image_studio import (
    ImageStudioRenderJobORM,
    ImageStudioSnapshotORM,
    ImageStudioWorkspaceORM,
)


class ImageStudioWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ImageStudioWorkspace]:
        rows = self.db.query(ImageStudioWorkspaceORM).order_by(ImageStudioWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: ImageStudioWorkspace) -> ImageStudioWorkspace:
        row = ImageStudioWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            creative_domains=workspace.creative_domains,
            output_goals=workspace.output_goals,
            linked_apps=workspace.linked_apps,
            linked_modules=workspace.linked_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> ImageStudioWorkspace | None:
        row = self.db.get(ImageStudioWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: ImageStudioStatus) -> ImageStudioWorkspace | None:
        row = self.db.get(ImageStudioWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ImageStudioWorkspaceORM) -> ImageStudioWorkspace:
        return ImageStudioWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=ImageStudioStatus(row.status),
            creative_domains=row.creative_domains or [],
            output_goals=row.output_goals or [],
            linked_apps=row.linked_apps or [],
            linked_modules=row.linked_modules or [],
        )


class ImageStudioSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: ImageStudioSnapshot) -> ImageStudioSnapshot:
        row = self.db.get(ImageStudioSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = ImageStudioSnapshotORM(workspace_id=snapshot.workspace_id)
        row.model_registry = snapshot.model_registry
        row.generation_modes = snapshot.generation_modes
        row.prompt_recipes = snapshot.prompt_recipes
        row.control_profiles = snapshot.control_profiles
        row.edit_profiles = snapshot.edit_profiles
        row.artifact_paths = snapshot.artifact_paths
        row.variant_scoring_rules = snapshot.variant_scoring_rules
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.creative_reliability_score = snapshot.creative_reliability_score
        row.deployment_readiness_score = snapshot.deployment_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ImageStudioSnapshot(
            workspace_id=row.workspace_id,
            model_registry=row.model_registry or [],
            generation_modes=row.generation_modes or [],
            prompt_recipes=row.prompt_recipes or [],
            control_profiles=row.control_profiles or [],
            edit_profiles=row.edit_profiles or [],
            artifact_paths=row.artifact_paths or [],
            variant_scoring_rules=row.variant_scoring_rules or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            creative_reliability_score=row.creative_reliability_score,
            deployment_readiness_score=row.deployment_readiness_score,
        )

    def get(self, workspace_id: str) -> ImageStudioSnapshot | None:
        row = self.db.get(ImageStudioSnapshotORM, workspace_id)
        if row is None:
            return None
        return ImageStudioSnapshot(
            workspace_id=row.workspace_id,
            model_registry=row.model_registry or [],
            generation_modes=row.generation_modes or [],
            prompt_recipes=row.prompt_recipes or [],
            control_profiles=row.control_profiles or [],
            edit_profiles=row.edit_profiles or [],
            artifact_paths=row.artifact_paths or [],
            variant_scoring_rules=row.variant_scoring_rules or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            creative_reliability_score=row.creative_reliability_score,
            deployment_readiness_score=row.deployment_readiness_score,
        )


class ImageStudioRenderJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_workspace(self, workspace_id: str) -> list[ImageStudioRenderJob]:
        rows = (
            self.db.query(ImageStudioRenderJobORM)
            .filter(ImageStudioRenderJobORM.workspace_id == workspace_id)
            .order_by(ImageStudioRenderJobORM.id.desc())
            .all()
        )
        return [self._to_domain(row) for row in rows]

    def create(self, job: ImageStudioRenderJob) -> ImageStudioRenderJob:
        row = ImageStudioRenderJobORM(
            id=job.id,
            workspace_id=job.workspace_id,
            mode=job.mode,
            prompt=job.prompt,
            negative_prompt=job.negative_prompt,
            model_name=job.model_name,
            width=job.width,
            height=job.height,
            steps=job.steps,
            guidance_scale=job.guidance_scale,
            seed=job.seed,
            control_type=job.control_type,
            source_asset_path=job.source_asset_path,
            mask_asset_path=job.mask_asset_path,
            output_asset_path=job.output_asset_path,
            status=job.status,
            metadata=job.metadata,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def update_status_and_output(
        self,
        job_id: str,
        status: str,
        output_asset_path: str = '',
        metadata: dict | None = None,
    ) -> ImageStudioRenderJob | None:
        row = self.db.get(ImageStudioRenderJobORM, job_id)
        if row is None:
            return None
        row.status = status
        if output_asset_path:
            row.output_asset_path = output_asset_path
        if metadata is not None:
            row.metadata = metadata
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, job_id: str) -> ImageStudioRenderJob | None:
        row = self.db.get(ImageStudioRenderJobORM, job_id)
        return None if row is None else self._to_domain(row)

    @staticmethod
    def _to_domain(row: ImageStudioRenderJobORM) -> ImageStudioRenderJob:
        return ImageStudioRenderJob(
            id=row.id,
            workspace_id=row.workspace_id,
            mode=row.mode,
            prompt=row.prompt,
            negative_prompt=row.negative_prompt,
            model_name=row.model_name,
            width=row.width,
            height=row.height,
            steps=row.steps,
            guidance_scale=row.guidance_scale,
            seed=row.seed,
            control_type=row.control_type,
            source_asset_path=row.source_asset_path,
            mask_asset_path=row.mask_asset_path,
            output_asset_path=row.output_asset_path,
            status=row.status,
            metadata=row.metadata or {},
        )
