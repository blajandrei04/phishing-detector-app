import { Component, OnInit, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PhishingService } from '../../core/services/phishing.service';

@Component({
  selector: 'app-admin-review',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-review.html',
  styleUrl: './admin-review.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AdminReviewComponent implements OnInit {
  private phishingService = inject(PhishingService);

  feedbackList = signal<any[]>([]);
  isLoading = signal<boolean>(true);

  ngOnInit() {
    this.loadFeedback();
  }

  loadFeedback() {
    this.isLoading.set(true);
    
    this.phishingService.getFeedback().subscribe({
      next: (data) => {
        this.feedbackList.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
      }
    });
  }

  dismissReport(id: number) {
    this.phishingService.deleteFeedback(id).subscribe({
      next: () => {
        this.feedbackList.update(list => list.filter(f => f.id !== id));
      }
    });
  }
}
