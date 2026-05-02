import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PhishingService } from '../../core/services/phishing.service';

@Component({
  selector: 'app-admin-review',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-review.html',
  styleUrl: './admin-review.scss'
})
export class AdminReviewComponent implements OnInit {
  private phishingService = inject(PhishingService);

  feedbackList: any[] = [];
  isLoading = true;

  ngOnInit() {
    this.loadFeedback();
  }

  loadFeedback() {
    this.isLoading = true;
    this.phishingService.getFeedback().subscribe({
      next: (data) => {
        this.feedbackList = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  dismissReport(id: number) {
    this.phishingService.deleteFeedback(id).subscribe({
      next: () => {
        this.feedbackList = this.feedbackList.filter(f => f.id !== id);
      }
    });
  }
}
