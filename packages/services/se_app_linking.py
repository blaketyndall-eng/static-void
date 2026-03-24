from packages.domain.app_builder import AppBlueprint
from packages.domain.software_engineering import EngineeringProject


def score_blueprint_project_match(blueprint: AppBlueprint, project: EngineeringProject) -> float:
    score = 0.0
    if blueprint.name.lower() == project.name.lower():
        score += 45.0

    blueprint_workflows = {item.lower() for item in blueprint.workflows}
    project_goals = {item.lower() for item in project.goals}
    score += min(len(blueprint_workflows & project_goals) * 8.0, 24.0)

    blueprint_views = {item.lower() for item in blueprint.primary_views}
    project_frameworks = {item.lower() for item in project.frameworks}
    score += min(len(blueprint_views & project_frameworks) * 4.0, 12.0)

    blueprint_sources = {item.lower() for item in blueprint.data_sources}
    project_languages = {item.lower() for item in project.languages}
    score += min(len(blueprint_sources & project_languages) * 4.0, 8.0)

    blueprint_desc = blueprint.description.lower()
    project_desc = project.description.lower()
    desc_overlap = 0
    for token in set(project_desc.split()):
        if len(token) > 4 and token in blueprint_desc:
            desc_overlap += 1
    score += min(desc_overlap * 2.0, 11.0)
    return min(score, 100.0)


def find_best_linked_project(blueprint: AppBlueprint, projects: list[EngineeringProject]) -> EngineeringProject | None:
    if not projects:
        return None
    scored = [(score_blueprint_project_match(blueprint, project), project) for project in projects]
    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_project = scored[0]
    return best_project if best_score >= 30.0 else None
