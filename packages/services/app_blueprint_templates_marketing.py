from packages.domain.app_builder import AppBlueprint, BuildPacket


def specialize_marketing_template(blueprint: AppBlueprint) -> BuildPacket:
    packet = blueprint.build_packet.model_copy(deep=True)
    slug = blueprint.name.lower().replace(" ", "_")

    packet.service_modules.extend([
        f"packages/services/{slug}_research_engine.py",
        f"packages/services/{slug}_content_engine.py",
        f"packages/services/{slug}_campaign_learning.py",
    ])
    packet.router_modules.extend([
        f"packages/routers/{slug}_research.py",
        f"packages/routers/{slug}_content.py",
        f"packages/routers/{slug}_analytics.py",
    ])
    packet.runtime_apps.extend([
        f"app_{slug}_console.py",
    ])
    packet.test_modules.extend([
        f"test_{slug}_research.py",
        f"test_{slug}_content.py",
    ])
    packet.observability_modules.extend([
        f"var/{slug}_marketing_telemetry.jsonl",
    ])
    return packet
