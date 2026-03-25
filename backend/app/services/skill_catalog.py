import yaml
import frontmatter
from pathlib import Path

from app.config import settings
from app.models import SkillMeta

# Korean description mapping for known skills
KO_DESCRIPTIONS: dict[str, str] = {
    # Core
    "bmad-brainstorming": "인터랙티브 브레인스토밍 세션. 창의적 기법을 활용한 아이디어 발상",
    "bmad-party-mode": "멀티 에이전트 오케스트레이션. 여러 전문가가 협업하여 문제 해결",
    "bmad-help": "BMAD 사용법 및 도움말",
    "bmad-init": "BMAD 프로젝트 설정 초기화",
    "bmad-index-docs": "프로젝트 문서 색인 생성",
    "bmad-shard-doc": "문서 분할 및 관리",
    "bmad-editorial-review-prose": "문서 문체/표현 리뷰",
    "bmad-editorial-review-structure": "문서 구조 리뷰",
    "bmad-review-adversarial-general": "적대적 관점에서의 품질 검토",
    "bmad-review-edge-case-hunter": "엣지 케이스 탐지 및 분석",
    "bmad-distillator": "LLM 최적화를 위한 문서 압축",
    "bmad-advanced-elicitation": "고급 요구사항 도출 기법",
    "bmad-agent-builder": "커스텀 에이전트/스킬 빌더",
    "bmad-builder-setup": "빌더 환경 설정",
    "bmad-workflow-builder": "워크플로우 빌더",
    # BMM - Agents
    "bmad-agent-analyst": "비즈니스 분석가. 도메인/시장/기술 리서치 및 분석",
    "bmad-agent-architect": "솔루션 아키텍트. 시스템 설계 및 아키텍처 수립",
    "bmad-agent-dev": "시니어 소프트웨어 엔지니어 (Amelia). 구현 및 개발",
    "bmad-agent-sm": "기술 스크럼 마스터 (Bob). 스프린트 관리 및 진행",
    "bmad-agent-pm": "프로젝트 매니저. 제품 기획 및 요구사항 관리",
    "bmad-agent-qa": "QA 전문가. 테스트 전략 및 품질 보증",
    "bmad-agent-ux-designer": "UX/프로덕트 디자이너. 사용자 경험 설계",
    "bmad-agent-tech-writer": "기술 문서 작성자. 문서화 및 기술 글쓰기",
    "bmad-agent-quick-flow-solo-dev": "솔로 개발자 플로우. 빠른 개발 워크플로우",
    # BMM - Skills
    "bmad-create-prd": "PRD(제품 요구사항 문서) 작성",
    "bmad-edit-prd": "기존 PRD 수정 및 업데이트",
    "bmad-create-architecture": "시스템 아키텍처 문서 작성",
    "bmad-create-story": "사용자 스토리 작성",
    "bmad-create-epics-and-stories": "에픽 및 스토리 체계 수립",
    "bmad-create-ux-design": "UX 디자인 산출물 생성",
    "bmad-dev-story": "개발 스토리 구현",
    "bmad-sprint-planning": "스프린트 플래닝 세션",
    "bmad-quick-dev": "빠른 개발 실행",
    "bmad-code-review": "코드 리뷰 수행",
    "bmad-correct-course": "프로젝트 방향 수정 및 재조정",
    "bmad-product-brief": "제품 브리프 작성",
    "bmad-document-project": "프로젝트 문서화",
    "bmad-domain-research": "도메인 리서치 및 분석",
    "bmad-technical-research": "기술 리서치 및 분석",
    # CIS
    "bmad-cis-problem-solving": "체계적 문제 해결 프레임워크",
    "bmad-cis-agent-brainstorming-coach": "브레인스토밍 코치. 창의적 사고 촉진",
    "bmad-cis-agent-creative-problem-solver": "창의적 문제 해결 전문가",
    "bmad-cis-storytelling": "스토리텔링 기법 활용",
    "bmad-cis-agent-storyteller": "스토리텔러. 내러티브 설계",
    "bmad-cis-agent-presentation-master": "프레젠테이션 마스터. 발표 자료 설계",
    # TEA
    "bmad-testarch-atdd": "ATDD(인수 테스트 주도 개발)",
    "bmad-testarch-test-design": "테스트 설계 및 전략",
    "bmad-testarch-automate": "테스트 자동화 구축",
    "bmad-testarch-ci": "CI/CD 테스트 파이프라인 통합",
    "bmad-testarch-nfr": "비기능 요구사항 테스트",
    # WDS
    "wds-0-project-setup": "프로젝트 초기 설정",
    "wds-0-alignment-signoff": "이해관계자 정렬 및 승인",
    "wds-1-project-brief": "프로젝트 브리프 작성",
    "wds-2-trigger-mapping": "트리거 매핑 설계",
    "wds-5-agentic-development": "에이전틱 개발 워크플로우",
    "wds-6-asset-generation": "에셋 생성 자동화",
    "wds-3-scenarios": "트리거 맵 기반 UX 시나리오 작성",
    "wds-4-ux-design": "시나리오 기반 상세 비주얼 사양 설계",
    "wds-7-design-system": "디자인 시스템 컴포넌트 및 토큰 관리",
    "wds-8-product-evolution": "기존 제품 개선 — 브라운필드 WDS 파이프라인",
    "wds-agent-freya-ux": "전략적 UX 디자이너. 디자인 씽킹 파트너",
    "wds-agent-saga-analyst": "전략적 비즈니스 분석가. 제품 디스커버리 파트너",
    # Core - 추가
    "bmad-check-implementation-readiness": "구현 준비 상태 검증. PRD/UX/아키텍처/에픽 완성도 확인",
    "bmad-generate-project-context": "AI 규칙이 포함된 project-context.md 생성",
    "bmad-market-research": "시장 조사. 경쟁사 및 고객 분석",
    "bmad-qa-generate-e2e-tests": "기존 기능 대상 E2E 자동화 테스트 생성",
    "bmad-retrospective": "에픽 완료 후 회고. 교훈 도출 및 성과 평가",
    "bmad-sprint-status": "스프린트 상태 요약 및 리스크 도출",
    "bmad-teach-me-testing": "테스트 학습. 구조화된 세션으로 점진적 교육",
    "bmad-testarch-framework": "Playwright/Cypress 테스트 프레임워크 초기화",
    "bmad-testarch-test-review": "베스트 프랙티스 기반 테스트 품질 리뷰",
    "bmad-testarch-trace": "추적성 매트릭스 생성 및 품질 게이트 판단",
    "bmad-validate-prd": "PRD 표준 검증",
    "bmad-tea": "마스터 테스트 아키텍트 및 품질 어드바이저 (Murray)",
    # CIS - 추가
    "bmad-cis-agent-design-thinking-coach": "디자인 씽킹 코치. 인간 중심 설계 프로세스 안내",
    "bmad-cis-agent-innovation-strategist": "혁신 전략가. 비즈니스 모델 혁신 및 파괴적 전략",
    "bmad-cis-design-thinking": "공감 기반 인간 중심 디자인 프로세스 가이드",
    "bmad-cis-innovation-strategy": "파괴적 기회 식별 및 비즈니스 모델 혁신 설계",
    # GDS - Game Development Suite
    "gds-agent-game-architect": "게임 시스템 아키텍트. 기술 아키텍처 및 엔진 설계",
    "gds-agent-game-designer": "게임 디자이너. 크리에이티브 비전 및 GDD 작성",
    "gds-agent-game-dev": "게임 개발자. 스토리 실행 및 코드 구현",
    "gds-agent-game-qa": "게임 QA 아키텍트. 테스트 자동화 및 품질 보증",
    "gds-agent-game-scrum-master": "게임 스크럼 마스터. 스프린트 플래닝 및 애자일 운영",
    "gds-agent-game-solo-dev": "인디 게임 개발자. 빠른 프로토타이핑 및 솔로 개발",
    "gds-agent-tech-writer": "기술 문서 전문가. 게임 프로젝트 문서화",
    "gds-brainstorm-game": "게임 브레인스토밍. 게임 특화 기법으로 아이디어 발상",
    "gds-check-implementation-readiness": "GDD/UX/아키텍처/에픽 정합성 검증",
    "gds-code-review": "코드 리뷰. 버그 및 품질 이슈 탐지",
    "gds-correct-course": "스프린트 방향 수정. 구현 이탈 시 재조정",
    "gds-create-epics-and-stories": "GDD 요구사항 기반 에픽 및 스토리 생성",
    "gds-create-game-brief": "게임 비전 정의를 위한 인터랙티브 게임 브리프 작성",
    "gds-create-gdd": "게임 디자인 문서(GDD) 작성. 메카닉 및 구현 가이드",
    "gds-create-narrative": "내러티브 문서 작성. 스토리 구조 및 세계관 설계",
    "gds-create-story": "구현에 필요한 컨텍스트를 담은 스토리 파일 생성",
    "gds-create-ux-design": "게임 UI/HUD UX 패턴 및 디자인 사양 설계",
    "gds-dev-story": "스토리 사양에 따른 구현 실행",
    "gds-document-project": "기존 게임 프로젝트 분석 및 문서화",
    "gds-domain-research": "게임 도메인 및 산업 리서치",
    "gds-e2e-scaffold": "E2E 테스트 인프라 스캐폴딩",
    "gds-game-architecture": "게임 아키텍처 설계. 엔진 시스템 및 네트워킹",
    "gds-generate-project-context": "AI 에이전트 일관성을 위한 project-context.md 생성",
    "gds-performance-test": "게임 성능 테스트 전략 설계",
    "gds-playtest-plan": "사용자 피드백을 위한 플레이테스트 계획 수립",
    "gds-quick-dev": "유연한 개발 워크플로우. 기술 사양 또는 직접 지시 실행",
    "gds-quick-dev-new-preview": "사용자 의도/GDD 요구/스토리/버그 수정 등 모든 구현",
    "gds-quick-spec": "구현 준비된 스토리를 포함한 기술 사양 작성",
    "gds-retrospective": "게임 개발 에픽 완료 후 회고 진행",
    "gds-sprint-planning": "에픽 파일 기반 스프린트 상태 생성/업데이트",
    "gds-sprint-status": "현재 스프린트 진행 상황 요약 및 리스크 도출",
    "gds-test-automate": "게임플레이 시스템 자동화 테스트 생성",
    "gds-test-design": "포괄적 게임 테스트 시나리오 작성",
    "gds-test-framework": "Unity/Unreal/Godot 게임 테스트 프레임워크 초기화",
    "gds-test-review": "테스트 품질 및 커버리지 리뷰",
}


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

        # Korean description: mapped or fallback
        description_ko = KO_DESCRIPTIONS.get(name, "")

        return SkillMeta(
            name=name,
            display_name=display_name,
            description=description,
            description_ko=description_ko,
            type=skill_type,
            icon=icon,
            module=module,
            role=role,
            capabilities=capabilities,
            has_workflow=has_workflow,
        )


skill_catalog = SkillCatalog()
