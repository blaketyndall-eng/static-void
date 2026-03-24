from packages.domain.app_builder import AppBlueprint, AppTemplateType, BuildPacket
from packages.services.app_blueprint_templates import specialize_build_packet
from packages.services.app_blueprint_templates_marketing import specialize_marketing_template


def specialize_build_packet_with_branches(blueprint: AppBlueprint) -> BuildPacket:
    packet = specialize_build_packet(blueprint)

    workflows = {item.lower() for item in blueprint.workflows}
    views = {item.lower() for item in blueprint.primary_views}
    description = blueprint.description.lower()
    data_sources = {item.lower() for item in blueprint.data_sources}

    marketing_hint = (
        blueprint.app_type in {AppTemplateType.operator_console, AppTemplateType.decision_workflow}
        and (
            "marketing" in description
            or "campaign" in description
            or "content" in description
            or "research" in description
            or "seo" in description
            or "email" in workflows
            or "landing_page" in workflows
            or "social" in workflows
            or "campaign" in workflows
            or "content" in workflows
            or "analytics" in views
            or "campaign" in data_sources
        )
    )

    if marketing_hint:
        bridge_blueprint = blueprint.model_copy(deep=True)
        bridge_blueprint.build_packet = packet
        return specialize_marketing_template(bridge_blueprint)

    return packet
