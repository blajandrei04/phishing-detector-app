import { Component, OnInit, inject, PLATFORM_ID, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PhishingService } from '../../core/services/phishing.service';
import { UrlValidatorService } from '../../core/services/url-validator.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent implements OnInit {
  private phishingService = inject(PhishingService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private urlValidator = inject(UrlValidatorService);

  urlToAnalyze = signal<string>('');
  isAnalyzing = signal<boolean>(false);
  analysisResult = signal<any>(null);
  analysisError = signal<string | null>(null);
  isLoading = signal<boolean>(true);

  // Activity chart data
  activityDays = signal<any[]>([]);
  activityMax = signal<number>(1);
  activityLoaded = signal<boolean>(false);

  summaryCards = signal<any[]>([
    {
      title: 'Total Scans',
      value: 0 as any,
      change: 'All time',
      changeType: 'increase',
      icon: 'bi-shield-check',
      color: 'blue',
    },
    {
      title: 'Threats Detected',
      value: 0 as any,
      change: '-',
      changeType: 'danger',
      icon: 'bi-shield-exclamation',
      color: 'red',
    },
    {
      title: 'Safe URLs',
      value: 0 as any,
      change: '-',
      changeType: 'increase',
      icon: 'bi-shield-lock',
      color: 'green',
    },
    {
      title: 'Suspicious',
      value: 0 as any,
      change: '-',
      changeType: 'neutral',
      icon: 'bi-question-octagon',
      color: 'purple',
    },
  ]);

  recentScans = signal<any[]>([]);

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.isLoading.set(true);

    this.phishingService.getStats().subscribe({
      next: (data) => {
        const currentCards = this.summaryCards();
        this.summaryCards.set([
          {
            ...currentCards[0],
            value: data.total_scans
          },
          {
            ...currentCards[1],
            value: data.phishing_count,
            change: data.total_scans > 0
              ? `${((data.phishing_count / data.total_scans) * 100).toFixed(1)}% of total`
              : 'No scans yet'
          },
          {
            ...currentCards[2],
            value: data.legitimate_count,
            change: data.total_scans > 0
              ? `${((data.legitimate_count / data.total_scans) * 100).toFixed(1)}% safe rate`
              : 'No scans yet'
          },
          {
            ...currentCards[3],
            value: data.suspicious_count,
            change: data.total_scans > 0
              ? `${((data.suspicious_count / data.total_scans) * 100).toFixed(1)}% of total`
              : 'No scans yet'
          }
        ]);
      }
    });

    this.phishingService.getHistory(0, 5).subscribe({
      next: (data) => {
        this.recentScans.set(data.items.map((item: any) => ({
          url: item.url,
          risk: item.verdict === 'phishing' ? 'High' : (item.verdict === 'suspicious' ? 'Medium' : 'Safe'),
          time: this.formatTimeAgo(new Date(item.created_at)),
          icon: item.verdict === 'phishing' ? 'bi-exclamation-octagon-fill'
            : item.verdict === 'suspicious' ? 'bi-exclamation-triangle-fill'
              : 'bi-check-circle-fill',
          riskColor: item.verdict === 'phishing' ? '#ef4444'
            : item.verdict === 'suspicious' ? '#f59e0b'
              : '#22c55e',
          score: item.score
        })));
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
      }
    });

    this.phishingService.getActivity(7).subscribe({
      next: (data) => {
        this.activityDays.set(data.days || []);
        this.activityMax.set(data.max_daily || 1);
        this.activityLoaded.set(true);
      },
      error: () => {
        this.activityLoaded.set(true);
      }
    });
  }

  submitUrl() {
    const validation = this.urlValidator.validate(this.urlToAnalyze());
    if (!validation.isValid) {
      this.analysisError.set(validation.errorMessage || 'Invalid URL');
      return;
    }

    let url = validation.formattedUrl;

    this.isAnalyzing.set(true);
    this.analysisError.set(null);
    this.analysisResult.set(null);

    this.phishingService.analyzeUrl({ url: url }).subscribe({
      next: (response) => {
        this.analysisResult.set(response);
        this.isAnalyzing.set(false);
        this.urlToAnalyze.set('');
        this.loadDashboardData();
      },
      error: (err) => {
        if (err.status === 422 && err.error?.detail) {
          const detail = err.error.detail;
          if (Array.isArray(detail)) {
            this.analysisError.set(detail.map((d: any) => d.msg).join('. '));
          } else {
            this.analysisError.set(String(detail));
          }
        } else {
          this.analysisError.set('Failed to analyze URL. Please check the backend connection.');
        }
        this.isAnalyzing.set(false);
      }
    });
  }

  formatTimeAgo(date: Date): string {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  }

  getDayLabel(dateStr: string): string {
    const date = new Date(dateStr + 'T12:00:00');
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  }

  viewFullReport() {
    const result = this.analysisResult();
    if (result && isPlatformBrowser(this.platformId)) {
      localStorage.setItem('lastResult', JSON.stringify(result));
      this.router.navigate(['/results']);
    }
  }
}
