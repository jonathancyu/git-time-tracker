from fastapi import FastAPI
from fastapi_camelcase import CamelModel
import mergelogs

class Commit(CamelModel):
    hash: str
    author: str
    email: str
    date: str
    message: str
    repo: str

    def __init__(self, commit: mergelogs.Commit):
        super().__init__(
            hash = commit.hash,
            author = commit.author,
            email = commit.email,
            date = commit.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            message = commit.message,
            repo = commit.repo_path
        )


app = FastAPI()

repo_paths = [
    "/Users/aa710193/workspace/projects/cec-controller/",
    "/Users/aa710193/workspace/SARS/SARSPortalUI/",
    "/Users/aa710193/workspace/SARS/SARSService/",
]

@app.get("/api/commits")
async def api_get_commits():    
    mapped_commits = [Commit(c) for c in mergelogs.get_commits_from_repos(repo_paths)]
    return {"result": mapped_commits}