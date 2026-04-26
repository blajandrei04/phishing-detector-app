import { Component, OnInit, PLATFORM_ID, Inject, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AnalyzeResponse } from '../../models/analyze-response.model';
import { PhishingService } from '../../core/services/phishing.service';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './results.component.html',
  styleUrl: './results.component.scss',
})
export class ResultsComponent implements OnInit {
  result: AnalyzeResponse | null = null;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  private phishingService = inject(PhishingService);

  isReporting = false;
  reportSuccess = false;
  reportError = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      const raw = localStorage.getItem('lastResult');
      this.result = raw ? JSON.parse(raw) : null;
    }
  }

  downloadPdf(): void {
    if (isPlatformBrowser(this.platformId)) {
      window.print();
    }
  }

  reportIncorrectVerdict(correctVerdict: string): void {
    if (!this.result) return;
    this.isReporting = true;
    this.reportError = '';

    const payload = {
      url: this.result.url,
      original_verdict: this.result.verdict,
      user_reported_verdict: correctVerdict,
      comments: 'Reported via Results UI'
    };

    this.phishingService.submitFeedback(payload).subscribe({
      next: () => {
        this.isReporting = false;
        this.reportSuccess = true;
        setTimeout(() => this.reportSuccess = false, 5000);
      },
      error: () => {
        this.isReporting = false;
        this.reportError = 'Failed to submit report. Please try again.';
      }
    });
  }

  getShapBarWidth(shapValue: number): number {
    if (!this.result?.shap_explanation?.shap_values?.length) return 0;
    const maxAbs = Math.max(
      ...this.result.shap_explanation.shap_values.map((s: any) => Math.abs(s.shap_value))
    );
    if (maxAbs === 0) return 0;
    return (Math.abs(shapValue) / maxAbs) * 45;
  }
}