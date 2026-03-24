from sqlalchemy.orm import Session

from packages.domain.apps import (
    AppAnalyticsSnapshot,
    AppFeedbackItem,
    AppHealthCheck,
    AppRecord,
    AppRun,
    AppStatus,
    AppType,
    DeploymentState,
)
from packages.storage.orm_apps import (
    AppAnalyticsSnapshotORM,
    AppFeedbackItemORM,
    AppHealthCheckORM,
    AppRecordORM,
    AppRunORM,
)


def _split_csv(value: str) -> list[str]:
    return [item for item in value.split(",") if item] if value else []


def _join_csv(values: list[str]) -> str:
    return ",".join(values)


class AppRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[AppRecord]:
        rows = self.db.query(AppRecordORM).order_by(AppRecordORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, app: AppRecord) -> AppRecord:
        row = AppRecordORM(
            id=app.id,
            name=app.name,
            app_type=app.app_type.value,
            owner=app.owner,
            description=app.description,
            status=app.status.value,
            deployment_state=app.deployment_state.value,
            version=app.version,
            runtime_url=app.runtime_url,
            tags_csv=_join_csv(app.tags),
            linked_brain_modules_csv=_join_csv(app.linked_brain_modules),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, app_id: str) -> AppRecord | None:
        row = self.db.get(AppRecordORM, app_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, app_id: str, status: AppStatus) -> AppRecord | None:
        row = self.db.get(AppRecordORM, app_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def update_deployment_state(self, app_id: str, deployment_state: DeploymentState) -> AppRecord | None:
        row = self.db.get(AppRecordORM, app_id)
        if row is None:
            return None
        row.deployment_state = deployment_state.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: AppRecordORM) -> AppRecord:
        return AppRecord(
            id=row.id,
            name=row.name,
            app_type=AppType(row.app_type),
            owner=row.owner,
            description=row.description,
            status=AppStatus(row.status),
            deployment_state=DeploymentState(row.deployment_state),
            version=row.version,
            runtime_url=row.runtime_url,
            tags=_split_csv(row.tags_csv),
            linked_brain_modules=_split_csv(row.linked_brain_modules_csv),
        )


class AppRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, run: AppRun) -> AppRun:
        row = AppRunORM(
            id=run.id,
            app_id=run.app_id,
            status=run.status,
            output_summary=run.output_summary,
            error_summary=run.error_summary,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AppRun(id=row.id, app_id=row.app_id, status=row.status, output_summary=row.output_summary, error_summary=row.error_summary)

    def list_for_app(self, app_id: str) -> list[AppRun]:
        rows = self.db.query(AppRunORM).filter(AppRunORM.app_id == app_id).all()
        return [AppRun(id=row.id, app_id=row.app_id, status=row.status, output_summary=row.output_summary, error_summary=row.error_summary) for row in rows]


class AppAnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: AppAnalyticsSnapshot) -> AppAnalyticsSnapshot:
        row = self.db.get(AppAnalyticsSnapshotORM, snapshot.app_id)
        if row is None:
            row = AppAnalyticsSnapshotORM(app_id=snapshot.app_id)
        row.sessions = snapshot.sessions
        row.active_users = snapshot.active_users
        row.completions = snapshot.completions
        row.failures = snapshot.failures
        row.outcome_quality_score = snapshot.outcome_quality_score
        row.latency_ms = snapshot.latency_ms
        row.model_cost_estimate = snapshot.model_cost_estimate
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AppAnalyticsSnapshot(
            app_id=row.app_id,
            sessions=row.sessions,
            active_users=row.active_users,
            completions=row.completions,
            failures=row.failures,
            outcome_quality_score=row.outcome_quality_score,
            latency_ms=row.latency_ms,
            model_cost_estimate=row.model_cost_estimate,
        )

    def get(self, app_id: str) -> AppAnalyticsSnapshot | None:
        row = self.db.get(AppAnalyticsSnapshotORM, app_id)
        if row is None:
            return None
        return AppAnalyticsSnapshot(
            app_id=row.app_id,
            sessions=row.sessions,
            active_users=row.active_users,
            completions=row.completions,
            failures=row.failures,
            outcome_quality_score=row.outcome_quality_score,
            latency_ms=row.latency_ms,
            model_cost_estimate=row.model_cost_estimate,
        )


class AppHealthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, check: AppHealthCheck) -> AppHealthCheck:
        row = self.db.get(AppHealthCheckORM, check.app_id)
        if row is None:
            row = AppHealthCheckORM(app_id=check.app_id)
        row.healthy = check.healthy
        row.error_count = check.error_count
        row.warning_count = check.warning_count
        row.notes_csv = _join_csv(check.notes)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AppHealthCheck(
            app_id=row.app_id,
            healthy=row.healthy,
            error_count=row.error_count,
            warning_count=row.warning_count,
            notes=_split_csv(row.notes_csv),
        )

    def get(self, app_id: str) -> AppHealthCheck | None:
        row = self.db.get(AppHealthCheckORM, app_id)
        if row is None:
            return None
        return AppHealthCheck(
            app_id=row.app_id,
            healthy=row.healthy,
            error_count=row.error_count,
            warning_count=row.warning_count,
            notes=_split_csv(row.notes_csv),
        )


class AppFeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, feedback: AppFeedbackItem) -> AppFeedbackItem:
        row = AppFeedbackItemORM(
            app_id=feedback.app_id,
            category=feedback.category,
            severity=feedback.severity,
            message=feedback.message,
        )
        self.db.add(row)
        self.db.commit()
        return feedback

    def list_for_app(self, app_id: str) -> list[AppFeedbackItem]:
        rows = self.db.query(AppFeedbackItemORM).filter(AppFeedbackItemORM.app_id == app_id).all()
        return [AppFeedbackItem(app_id=row.app_id, category=row.category, severity=row.severity, message=row.message) for row in rows]
