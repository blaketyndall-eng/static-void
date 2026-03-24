from packages.domain.app_builder import AppBlueprint, AppTemplateType, BuildPacket


def specialize_build_packet(blueprint: AppBlueprint) -> BuildPacket:
    packet = blueprint.build_packet.model_copy(deep=True)
    slug = blueprint.name.lower().replace(" ", "_")

    if blueprint.app_type == AppTemplateType.operator_console:
        packet.service_modules.extend([
            f"packages/services/{slug}_analytics.py",
            f"packages/services/{slug}_health.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_metrics.py",
            f"packages/routers/{slug}_views.py",
        ])
    elif blueprint.app_type == AppTemplateType.analyst_tool:
        packet.service_modules.extend([
            f"packages/services/{slug}_engines.py",
            f"packages/services/{slug}_learning.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_operator.py",
            f"packages/routers/{slug}_learning.py",
        ])
    elif blueprint.app_type == AppTemplateType.decision_workflow:
        packet.service_modules.extend([
            f"packages/services/{slug}_workflow.py",
            f"packages/services/{slug}_recommendations.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_workflow.py",
            f"packages/routers/{slug}_summary.py",
        ])
    elif blueprint.app_type == AppTemplateType.monitoring_dashboard:
        packet.service_modules.extend([
            f"packages/services/{slug}_alerts.py",
            f"packages/services/{slug}_monitoring.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_alerts.py",
            f"packages/routers/{slug}_dashboard.py",
        ])
    elif blueprint.app_type == AppTemplateType.reporting_app:
        packet.service_modules.extend([
            f"packages/services/{slug}_reports.py",
            f"packages/services/{slug}_exports.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_reports.py",
            f"packages/routers/{slug}_exports.py",
        ])
    elif blueprint.app_type == AppTemplateType.consumer_decision_app:
        packet.service_modules.extend([
            f"packages/services/{slug}_personalization.py",
            f"packages/services/{slug}_feedback.py",
        ])
        packet.router_modules.extend([
            f"packages/routers/{slug}_consumer_views.py",
            f"packages/routers/{slug}_feedback.py",
        ])

    return packet
