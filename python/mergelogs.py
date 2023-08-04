import re
import subprocess
import os

from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
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

class Commit:
    hash: str
    author: str
    email: str
    date: datetime.date
    message: str
    repo_path: str

    def __init__(self, commit_text: str, repo_path: str):
        lines = (seq(commit_text.split("\n"))
            .map(str.strip)
        )
        
        self.hash = get_line(lines, "commit").split(" ")[0]
        self.author, self.email = Commit.extract_author_and_email(get_line(lines, "Author:"))
        self.date = datetime.strptime(get_line(lines, "Date:"), "%a %b %d %H:%M:%S %Y %z").astimezone(timezone.utc)
        self.message = f"\n{INDENT*2}".join(Commit.get_message(commit_text))
        self.repo_path = ""
    
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

    # Formatting
    def pretty_date(self):
        return self.date.astimezone(get_localzone()) \
            .strftime("%a %b %d")
    
    def pretty_time(self):
        return self.date.astimezone(get_localzone()) \
            .strftime("%H:%M")
    
    def pretty_repo(self):
        return self.repo.split("/")[-1]

    def format(self):
        return COMMIT_FORMAT.format(
            date = self.pretty_date(),
            time = self.pretty_time(),
            message = self.message,
            author = self.author,
            repo = self.pretty_repo
            ) + "\n"
    

def get_commits(repo_path: str):
    print(repo_path)
    os.chdir(repo_path)
    
    log = subprocess.check_output(
        ["git", "log"], universal_newlines=True
    )
    commits_text = re.split(r"(?=\bcommit [a-f0-9]+\b)", log)
    commits = ( seq(commits_text) 
        .map(str.strip) 
        .filter_not(is_empty)
        .map(lambda c: Commit(c, repo_path))
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
    timeline = sorted(commits, key = lambda x: x.date, reverse=True)

    cutoff = (datetime.now(timezone.utc) - time_delta)
    first_old_entry = next(i for i, c in enumerate(timeline) if c.date < cutoff)
    if first_old_entry is not None:
        timeline = timeline[:first_old_entry]
    
    dates: OrderedDict[str, str] = {}
    for commit in timeline:
        date = commit.pretty_date()
        dates[date] = dates.get(date, f"{date}\n")
        dates[date] += commit.format() + "\n"

    return "\n".join(dates.values())

