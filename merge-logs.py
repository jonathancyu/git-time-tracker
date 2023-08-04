import re
import subprocess
import os

from datetime import datetime
from functional import seq

AUTHOR_TEXT = "Author:"
DATE_TEXT = "Date:"
COMMIT_FORMAT = '''{date} {message}
    {author}
'''
is_empty = lambda x: (not x) or x.isspace()

class Commit:
    hash: str
    author: str
    email: str
    date: datetime.date
    message: str

    def __init__(self, commit_text: str):
        lines = (seq(commit_text.split("\n"))
            .map(str.strip)
            .filter_not(is_empty)
        )
        
        self.hash = lines[0].split(" ")[1]
        self.author, self.email = Commit.extract_author_and_email(lines[1])
        date_str = lines[2][len(DATE_TEXT)+1:].strip()
        self.date = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z")
        self.message = "<newline>".join(lines[3:])

    def pretty_date(self):
        return self.date.strftime("%a %b %d at %H:M")


    def format(self):
        return COMMIT_FORMAT.format(
            date = self.pretty_date(),
            message = self.message,
            author = self.author
            )
    

    def extract_author_and_email(line: str):
        print(line)
        email_pos, email_end = line.index("<"), line.index(">")
        return line[len(AUTHOR_TEXT):email_pos].strip(), \
               line[email_pos+1:email_end]


def get_commits(repo_path: str):
    os.chdir(repo_path)
    
    log = subprocess.check_output(
        ["git", "log"], universal_newlines=True
    )
    commits = re.split(r"(?=\bcommit [a-f0-9]+\b)", log)
    return ( seq(commits) 
        .map(str.strip) 
        .filter_not(is_empty)
        .map(Commit)
    )

def get_commits_from_repos(repo_paths: list[str]):
    all_commits = []
    for repo_path in repo_paths:
        commits = get_commits(repo_path)
        all_commits.extend(commits)
        
    return all_commits

def make_timeline(commits: list[Commit]):
    timeline = sorted(commits, key = lambda x: x.date, reverse=True)
    formatted_timeline = map(Commit.format, timeline)
    return "\n |\n".join(formatted_timeline)


repo_paths = [
    "/Users/aa710193/workspace/projects/cec-controller/",
    "/Users/aa710193/workspace/SARS/SARSPortalUI/",
    # add as many repositories as you need
]

commits = get_commits_from_repos(repo_paths)

print(make_timeline(commits))