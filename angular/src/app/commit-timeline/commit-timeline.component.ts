import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http'
import { TimelineUtil } from './timeline-util';

type CommitModel = {
  hash: string;
  author: string;
  email: string;
  date: string;
  message: string;
  repoPath: string;
}

type Day = {
  date: string;
  commits: CommitModel[]
}
class RepositoryManager {
  private defaultHue = "100";
  private colorIndex: number = 0;
  private colorMap: Map<string, string[]> = new Map();

  constructor(private colorList: string[][]) { }

  add(repo: string) {
    if (!this.colorMap.has(repo)) {
      this.colorMap.set(repo, this.colorList[this.colorIndex]);
      this.colorIndex = (this.colorIndex + 1) % this.colorList.length;
    }
  }

  getColor(repo: string): string[] {
    return this.colorMap.get(repo) || ["",""];
  }
}

const repos = new RepositoryManager([
  ["bg-indigo-100", "bg-indigo-200"],
  ["bg-green-100", "bg-green-200"],
  ["bg-pink-100", "bg-pink-200"],
  ["bg-light-blue-100", "bg-light-blue-200"],
  ["bg-amber-100", "bg-amber-200"],
  ["bg-yellow-100", "bg-yellow-200"],
])

class Commit {
  hash: string;
  author: string;
  email: string;
  date: Date;
  message: string;
  repoPath: string;

  hover: boolean = false;
  selected: boolean = false;


  constructor(commit: CommitModel) {
    this.hash = commit.hash;
    this.author = commit.author;
    this.email = commit.email;
    this.date = new Date(commit.date);
    this.message = commit.message;
    this.repoPath = commit.repoPath;

    repos.add(this.repoPath);
  }

  get prettyTime(): string {
    let hour = this.date.getHours();
    let prettyHour = ((hour - 1) % 12 + 1)
    let minute = this.date.getMinutes();
    let meridiem = hour < 12 ? "AM" : "PM";
    return `${prettyHour}:${TimelineUtil.padZero(minute)} ${meridiem}`
  }

  get prettyRepo(): string {
    return this.repoPath.split("/")
      .filter(x => x.length > 0)
      .slice(-1)[0];
  }

  get repoColor(): string[] {
    return repos.getColor(this.repoPath);
  }


  get currentClass(): string {
    return this.repoColor[Number(this.selected)];
  }
}

const monthNames = ["January", "February", "March",
  "April", "May", "June",
  "July", "August", "September",
  "October", "November", "December"
];
class DayWrapper {
  date: Date;
  commits: Commit[];

  constructor(day: Day) {
    this.date = new Date(day.date);
    this.commits = day.commits.map(c => new Commit(c));
  }

  prettyDate(): string {
    return this.date.getDay() + " "
      + monthNames[this.date.getMonth()].substring(0, 3);
  }

}


@Component({
  selector: 'app-commit-timeline',
  templateUrl: './commit-timeline.component.html',
  styleUrls: ['./commit-timeline.component.css']
})
export class CommitTimelineComponent {

  timeline: DayWrapper[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get<Day[]>("http://localhost:8000/api/timeline").subscribe(
      timeline => {
        this.timeline = timeline.map(day => new DayWrapper(day)) 
      }
    )
  }

  toggleCommit(commit: Commit) {
    commit.selected = !commit.selected;
  }

  hoverCommit(commit: Commit, value: boolean) {
    commit.hover = value;
    console.log(value)
  }
}
