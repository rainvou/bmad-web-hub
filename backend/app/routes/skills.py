from fastapi import APIRouter, HTTPException, Query

from app.models import SkillMeta
from app.services.skill_catalog import skill_catalog

router = APIRouter(tags=["skills"])


@router.get("/skills", response_model=list[SkillMeta])
async def list_skills(
    module: str | None = Query(None),
    type: str | None = Query(None),
):
    skills = skill_catalog.skills
    if module:
        skills = [s for s in skills if s.module == module]
    if type:
        skills = [s for s in skills if s.type == type]
    return skills


@router.get("/skills/{name}", response_model=SkillMeta)
async def get_skill(name: str):
    skill = skill_catalog.get(name)
    if not skill:
        raise HTTPException(404, f"Skill '{name}' not found")
    return skill
