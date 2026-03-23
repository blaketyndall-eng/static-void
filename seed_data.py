from db_session import SessionLocal
from domain_models import EvaluationRecord, OpportunityRecord, SourceRecord, SourceType, new_id
from repository_evaluations import EvaluationRepository
from repository_opportunities import OpportunityRepository
from repository_sources import SourceRepository


def seed() -> None:
    db = SessionLocal()
    source_repo = SourceRepository(db)
    opportunity_repo = OpportunityRepository(db)
    evaluation_repo = EvaluationRepository(db)

    source = source_repo.create(
        source=SourceRecord(
            id=new_id("src"),
            name="G2",
            source_type=SourceType.website,
            trust_score=0.82,
            freshness_label="weekly",
            tags=["reviews", "software"],
        )
    )

    opportunity_repo.create(
        opportunity=OpportunityRecord(
            id=new_id("opp"),
            title="Decision intelligence wedge",
            summary="Use messy vendor and market signals to structure shortlist creation.",
            source_ids=[source.id],
            themes=["signals", "procurement"],
            score=88,
        )
    )

    evaluation_repo.create(
        evaluation=EvaluationRecord(
            id=new_id("eval"),
            title="AI governance platform review",
            decision_owner="blake",
            criteria=[{"name": "Security", "weight": 0.35}],
        )
    )

    db.close()


if __name__ == "__main__":
    seed()
    print("seed data created")
