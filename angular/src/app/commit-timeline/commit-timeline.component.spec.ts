import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommitTimelineComponent } from './commit-timeline.component';

describe('CommitTimelineComponent', () => {
  let component: CommitTimelineComponent;
  let fixture: ComponentFixture<CommitTimelineComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CommitTimelineComponent]
    });
    fixture = TestBed.createComponent(CommitTimelineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
