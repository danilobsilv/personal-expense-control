import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv(".env.local")

def run(host: str = os.getenv("LOCALHOST"), port: int = os.getenv("LOCALHOST_PORT"), reload: bool = True) -> None:
    uvicorn.run(
        "app.setup:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(Path(__file__).parent / "app")] if reload else None,
        log_level="info",
    )

if __name__ == "__main__":
    run()
