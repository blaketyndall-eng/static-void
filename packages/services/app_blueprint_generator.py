from packages.domain.app_builder import AppBlueprint, AppTemplateType, BuildPacket, ScaffoldPlan


def generate_build_packet(app_type: AppTemplateType, name: str) -> BuildPacket:
    slug = name.lower().replace(" ", "_")
    return BuildPacket(
        domain_modules=[f"packages/domain/{slug}.py"],
        contract_modules=[f"packages/contracts/{slug}.py"],
        storage_modules=[f"packages/storage/orm_{slug}.py"],
        repository_modules=[f"packages/repositories/{slug}.py"],
        service_modules=[f"packages/services/{slug}_services.py"],
        router_modules=[f"packages/routers/backend_{slug}.py"],
        runtime_apps=[f"app_{slug}.py"],
        test_modules=[f"test_{slug}.py"],
        observability_modules=[f"var/{slug}_telemetry.jsonl"],
    )


def build_blueprint(
    *,
    name: str,
    app_type: AppTemplateType,
    description: str = "",
    target_users: list[str] | None = None,
    workflows: list[str] | None = None,
    required_engines: list[str] | None = None,
    primary_views: list[str] | None = None,
    data_sources: list[str] | None = None,
    notes: str = "",
) -> AppBlueprint:
    return AppBlueprint(
        name=name,
        app_type=app_type,
        description=description,
        target_users=target_users or [],
        workflows=workflows or [],
        required_engines=required_engines or [],
        primary_views=primary_views or [],
        data_sources=data_sources or [],
        build_packet=generate_build_packet(app_type, name),
        notes=notes,
    )


def generate_scaffold_plan(
    blueprint: AppBlueprint,
    *,
    include_observability: bool = True,
    include_tests: bool = True,
    include_runtime_apps: bool = True,
    tech_debt_items: list[str] | None = None,
) -> ScaffoldPlan:
    packet = blueprint.build_packet
    generated_files = []
    generated_files.extend(packet.domain_modules)
    generated_files.extend(packet.contract_modules)
    generated_files.extend(packet.storage_modules)
    generated_files.extend(packet.repository_modules)
    generated_files.extend(packet.service_modules)
    generated_files.extend(packet.router_modules)
    if include_runtime_apps:
        generated_files.extend(packet.runtime_apps)
    if include_tests:
        generated_files.extend(packet.test_modules)
    if include_observability:
        generated_files.extend(packet.observability_modules)

    steps = [
        f"Define {blueprint.name} domain and contracts.",
        "Add storage and repository modules.",
        "Implement service and router layers.",
        "Compose runtime app surface.",
    ]
    if include_tests:
        steps.append("Add tests and shared helpers.")
    if include_observability:
        steps.append("Add telemetry and observability hooks.")

    return ScaffoldPlan(
        blueprint_id=blueprint.id,
        summary=f"Scaffold plan for {blueprint.name} using {blueprint.app_type.value} template.",
        steps=steps,
        recommended_frameworks=["FastAPI", "Pydantic", "SQLAlchemy", "router-based packaged runtime"],
        generated_files=generated_files,
        tech_debt_items=tech_debt_items or [],
    )
