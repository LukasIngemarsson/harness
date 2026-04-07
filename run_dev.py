"""Development server with reload, excluding .workspace/ from file watcher."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        reload=True,
        reload_excludes=[".workspace/*", ".logs/*", ".notes/*"],
    )
