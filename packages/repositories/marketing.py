from sqlalchemy.orm import Session

from packages.domain.marketing import (
    ContentAsset,
    ContentAssetType,
    MarketingAnalyticsSnapshot,
    MarketingProject,
    MarketingProjectStatus,
    MarketingProjectType,
    MarketingResearchRecord,
)
from packages.storage.orm_marketing import (
    ContentAssetORM,
    MarketingAnalyticsSnapshotORM,
    MarketingProjectORM,
    MarketingResearchRecordORM,
)


class MarketingProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[MarketingProject]:
        rows = self.db.query(MarketingProjectORM).order_by(MarketingProjectORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, project: MarketingProject) -> MarketingProject:
        row = MarketingProjectORM(
            id=project.id,
            name=project.name,
            project_type=project.project_type.value,
            owner=project.owner,
            description=project.description,
            status=project.status.value,
            audience=project.audience,
            channels=project.channels,
            goals=project.goals,
            linked_apps=project.linked_apps,
            linked_brain_modules=project.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, project_id: str) -> MarketingProject | None:
        row = self.db.get(MarketingProjectORM, project_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, project_id: str, status: MarketingProjectStatus) -> MarketingProject | None:
        row = self.db.get(MarketingProjectORM, project_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: MarketingProjectORM) -> MarketingProject:
        return MarketingProject(
            id=row.id,
            name=row.name,
            project_type=MarketingProjectType(row.project_type),
            owner=row.owner,
            description=row.description,
            status=MarketingProjectStatus(row.status),
            audience=row.audience or [],
            channels=row.channels or [],
            goals=row.goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class MarketingResearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, record: MarketingResearchRecord) -> MarketingResearchRecord:
        row = self.db.get(MarketingResearchRecordORM, record.project_id)
        if row is None:
            row = MarketingResearchRecordORM(project_id=record.project_id)
        row.market_summary = record.market_summary
        row.competitor_summary = record.competitor_summary
        row.audience_insights = record.audience_insights
        row.channel_insights = record.channel_insights
        row.source_notes = record.source_notes
        row.opportunity_score = record.opportunity_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return MarketingResearchRecord(
            project_id=row.project_id,
            market_summary=row.market_summary,
            competitor_summary=row.competitor_summary,
            audience_insights=row.audience_insights or [],
            channel_insights=row.channel_insights or [],
            source_notes=row.source_notes or [],
            opportunity_score=row.opportunity_score,
        )

    def get(self, project_id: str) -> MarketingResearchRecord | None:
        row = self.db.get(MarketingResearchRecordORM, project_id)
        if row is None:
            return None
        return MarketingResearchRecord(
            project_id=row.project_id,
            market_summary=row.market_summary,
            competitor_summary=row.competitor_summary,
            audience_insights=row.audience_insights or [],
            channel_insights=row.channel_insights or [],
            source_notes=row.source_notes or [],
            opportunity_score=row.opportunity_score,
        )


class ContentAssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, asset: ContentAsset) -> ContentAsset:
        row = ContentAssetORM(
            project_id=asset.project_id,
            asset_type=asset.asset_type.value,
            title=asset.title,
            status=asset.status,
            target_channel=asset.target_channel,
            source_brief=asset.source_brief,
            generated_outline=asset.generated_outline,
            body=asset.body,
            call_to_action=asset.call_to_action,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ContentAsset(
            project_id=row.project_id,
            asset_type=ContentAssetType(row.asset_type),
            title=row.title,
            status=row.status,
            target_channel=row.target_channel,
            source_brief=row.source_brief,
            generated_outline=row.generated_outline or [],
            body=row.body,
            call_to_action=row.call_to_action,
        )

    def list_for_project(self, project_id: str) -> list[ContentAsset]:
        rows = self.db.query(ContentAssetORM).filter(ContentAssetORM.project_id == project_id).all()
        return [
            ContentAsset(
                project_id=row.project_id,
                asset_type=ContentAssetType(row.asset_type),
                title=row.title,
                status=row.status,
                target_channel=row.target_channel,
                source_brief=row.source_brief,
                generated_outline=row.generated_outline or [],
                body=row.body,
                call_to_action=row.call_to_action,
            )
            for row in rows
        ]


class MarketingAnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: MarketingAnalyticsSnapshot) -> MarketingAnalyticsSnapshot:
        row = self.db.get(MarketingAnalyticsSnapshotORM, snapshot.project_id)
        if row is None:
            row = MarketingAnalyticsSnapshotORM(project_id=snapshot.project_id)
        row.impressions = snapshot.impressions
        row.clicks = snapshot.clicks
        row.conversions = snapshot.conversions
        row.engagement_rate = snapshot.engagement_rate
        row.content_velocity = snapshot.content_velocity
        row.quality_score = snapshot.quality_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return MarketingAnalyticsSnapshot(
            project_id=row.project_id,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            engagement_rate=row.engagement_rate,
            content_velocity=row.content_velocity,
            quality_score=row.quality_score,
        )

    def get(self, project_id: str) -> MarketingAnalyticsSnapshot | None:
        row = self.db.get(MarketingAnalyticsSnapshotORM, project_id)
        if row is None:
            return None
        return MarketingAnalyticsSnapshot(
            project_id=row.project_id,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            engagement_rate=row.engagement_rate,
            content_velocity=row.content_velocity,
            quality_score=row.quality_score,
        )
