import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http'

type Commit = {
  hash: string;
  author: string;
  email: string;
  date: string;
  message: string;
  repo: string;
}

type Day = {
  date: string;
  commits: Commit[]
}

function padZero(x: number): string {
  return `${x > 9 ? '' : '0'}${x}`
}


class CommitWrapper {
  hash: string;
  author: string;
  email: string;
  date: Date;
  message: string;
  repo: string;
  
  constructor(commit: Commit) {
    this.hash = commit.hash
    this.author = commit.author
    this.email = commit.email
    this.date = new Date(commit.date)
    this.message = commit.message
    this.repo = commit.repo
  }

  
  prettyTime(): string {
    let hour = this.date.getHours();
    let prettyHour = ((hour-1)%12+1)
    let minute = this.date.getMinutes();
    let meridiem = hour < 12 ? "AM" : "PM";
    return `${prettyHour}:${padZero(minute)} ${meridiem}`
  }
}

const monthNames = ["January", "February", "March", 
"April", "May", "June",
"July", "August", "September", 
"October", "November", "December"
];
class DayWrapper {
  date: Date;
  commits: CommitWrapper[];

  constructor(day: Day) {
    this.date = new Date(day.date);
    this.commits = day.commits.map(c => new CommitWrapper(c));
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
        this.timeline = timeline.map(day => new DayWrapper(day));
        console.log(this.timeline);
      }
    )
  }
}
