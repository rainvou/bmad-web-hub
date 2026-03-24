import yaml
import frontmatter
from pathlib import Path

from app.config import settings
from app.models import SkillMeta


class SkillCatalog:
    def __init__(self):
        self._skills: list[SkillMeta] = []

    @property
    def skills(self) -> list[SkillMeta]:
        return self._skills

    async def scan(self) -> list[SkillMeta]:
        self._skills = []
        skills_dir = settings.SKILLS_DIR
        if not skills_dir.exists():
            return self._skills

        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue

            meta = self._parse_skill(skill_dir)
            if meta:
                self._skills.append(meta)

        return self._skills

    def get(self, name: str) -> SkillMeta | None:
        for s in self._skills:
            if s.name == name:
                return s
        return None

    def _parse_skill(self, skill_dir: Path) -> SkillMeta | None:
        skill_md = skill_dir / "SKILL.md"
        manifest_yaml = skill_dir / "bmad-skill-manifest.yaml"

        name = skill_dir.name
        description = ""
        display_name = name
        skill_type = "skill"
        icon = ""
        module = "core"
        role = ""
        capabilities = ""
        has_workflow = (skill_dir / "workflow.md").exists()

        # Parse SKILL.md frontmatter
        if skill_md.exists():
            try:
                post = frontmatter.load(str(skill_md))
                fm = post.metadata
                name = fm.get("name", name)
                description = fm.get("description", "")
            except Exception:
                pass

        # Parse manifest YAML
        if manifest_yaml.exists():
            try:
                with open(manifest_yaml) as f:
                    manifest = yaml.safe_load(f)
                if manifest:
                    display_name = manifest.get("displayName", display_name)
                    skill_type = manifest.get("type", skill_type)
                    icon = manifest.get("icon", icon)
                    module = manifest.get("module", module)
                    role = manifest.get("role", role)
                    capabilities = manifest.get("capabilities", capabilities)
            except Exception:
                pass

        if not display_name or display_name == name:
            display_name = name.replace("bmad-", "").replace("-", " ").title()

        return SkillMeta(
            name=name,
            display_name=display_name,
            description=description,
            type=skill_type,
            icon=icon,
            module=module,
            role=role,
            capabilities=capabilities,
            has_workflow=has_workflow,
        )


skill_catalog = SkillCatalog()
