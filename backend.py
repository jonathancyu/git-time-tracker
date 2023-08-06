import re
import subprocess
import os
import uvicorn

from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi_camelcase import CamelModel
from fastapi.middleware.cors import CORSMiddleware
from functional import seq
from tzlocal import get_localzone

INDENT = "  "
COMMIT_FORMAT = INDENT + "{time} - {author}\n" + INDENT*2 + "{message}"
is_empty = lambda x: (not x) or x.isspace()

def get_line(lines: list[str], prefix: str):
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix)+1:].strip()
    raise IndexError

class Commit(CamelModel):
    hash: str
    author: str
    email: str
    date: str
    message: str
    repo_path: str

    def new(commit_text: str, repo_path: str):
        lines = (seq(commit_text.split("\n"))
            .map(str.strip)
        )
        
        hash = get_line(lines, "commit").split(" ")[0]
        author, email = Commit.extract_author_and_email(get_line(lines, "Author:"))
        date = get_line(lines, "Date:")
        message = f"\n{INDENT*2}".join(Commit.get_message(commit_text))
        return Commit(hash, author, email, date, message, repo_path)
        

    def __init__(self, 
                 hash: str,
                 author: str,
                 email: str,
                 date: str,
                 message: str,
                 repo_path: str):
        date = datetime.strptime(date, "%a %b %d %H:%M:%S %Y %z").astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        super().__init__(
            hash = hash,
            author = author,
            email = email,
            date = date,
            message = message,
            repoPath = repo_path
        )

    def set_repo_path(self, repo_path: str):
        self.repo_path = repo_path
    
    # Helper
    def extract_author_and_email(line: str):
        email_pos, email_end = line.index("<"), line.index(">")
        return line[:email_pos].strip(), \
               line[email_pos+1:email_end]
    
    def get_message(commit_text: str):
        message = commit_text[commit_text.index("    "):]

        return (seq(message.strip().split("\n"))
                .map(str.strip)
                .filter_not(is_empty)
        )

    # Getters
    def get_datetime(self) -> datetime:
        return datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ")
    
    def get_day(self) -> str:
        return self.get_datetime().strftime("%a %b %d")



class Day(CamelModel):
    date: str
    commits: list[Commit]
    def __init__(self, date: str, commits: list[Commit]):
        super().__init__(
            date = date,
            commits = commits
        )

    

def get_commits(repo_path: str):
    os.chdir(repo_path)
    
    log = subprocess.check_output(
        ["git", "log"], universal_newlines=True
    )
    commits_text = re.split(r"(?=\bcommit [a-f0-9]+\b)", log)
    commits = ( seq(commits_text) 
        .map(str.strip) 
        .filter_not(is_empty)
        .map(lambda c: Commit.new(c, repo_path))
    )
    return commits

def get_commits_from_repos(repo_paths: list[str]):
    all_commits = []
    for repo_path in repo_paths:
        commits = get_commits(repo_path)
        all_commits.extend(commits)
        
    return all_commits

def make_timeline(commits: list[Commit],
                  time_delta = timedelta(days=7)):
    sorted_commits = sorted(commits, key = lambda x: x.get_datetime(), reverse=True)

    cutoff = (datetime.now() - time_delta)
    first_old_entry = next(i for i, c in enumerate(sorted_commits) if c.get_datetime() < cutoff)
    if first_old_entry is not None:
        sorted_commits = sorted_commits[:first_old_entry]
    
    timeline_dict: OrderedDict[str, list[Commit]] = OrderedDict()
    for commit in sorted_commits:
        date = commit.get_day()
        timeline_dict[date] = timeline_dict.get(date, [])
        timeline_dict[date].append(commit)

    timeline: list[Day] = []
    for day, commits in timeline_dict.items():
        date = commits[0].date
        timeline.append(Day(date, commits))
    print(timeline)
    return timeline
    

repo_paths = ["/Users/aa710193/workspace/projects/cec-controller/",
"/Users/aa710193/workspace/SARS/SARSPortalUI/",
"/Users/aa710193/workspace/SARS/SARSService/",]
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/commits")
async def api_get_commits():    
    commits = get_commits_from_repos(repo_paths)
    return commits

@app.get("/api/timeline")
async def api_get_timeline():    
    commits = get_commits_from_repos(repo_paths)
    timeline = make_timeline(commits)
    return timeline

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)