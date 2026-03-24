from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    SKILLS_DIR: Path = Path("")
    OUTPUT_DIR: Path = Path("")
    CLAUDE_BIN: Path = Path("/home/axz/.local/bin/claude")
    DB_PATH: Path = Path("")

    def model_post_init(self, __context) -> None:
        if self.SKILLS_DIR == Path(""):
            self.SKILLS_DIR = self.PROJECT_ROOT / ".claude" / "skills"
        if self.OUTPUT_DIR == Path(""):
            self.OUTPUT_DIR = self.PROJECT_ROOT / "_bmad-output"
        if self.DB_PATH == Path(""):
            self.DB_PATH = self.PROJECT_ROOT / "backend" / "bmad.db"


settings = Settings()
