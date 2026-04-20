import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PhishingService } from '../../core/services/phishing.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
})
export class DashboardComponent implements OnInit {
  private phishingService = inject(PhishingService);
  private cdr = inject(ChangeDetectorRef);

  urlToAnalyze: string = '';
  isAnalyzing: boolean = false;
  analysisResult: any = null;
  analysisError: string | null = null;
  isLoading: boolean = true;

  // Activity chart data
  activityDays: any[] = [];
  activityMax: number = 1;
  activityLoaded: boolean = false;

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.isLoading = true;

    this.phishingService.getStats().subscribe({
      next: (data) => {
        this.summaryCards = [
          {
            ...this.summaryCards[0],
            value: data.total_scans
          },
          {
            ...this.summaryCards[1],
            value: data.phishing_count,
            change: data.total_scans > 0
              ? `${((data.phishing_count / data.total_scans) * 100).toFixed(1)}% of total`
              : 'No scans yet'
          },
          {
            ...this.summaryCards[2],
            value: data.legitimate_count,
            change: data.total_scans > 0
              ? `${((data.legitimate_count / data.total_scans) * 100).toFixed(1)}% safe rate`
              : 'No scans yet'
          },
          {
            ...this.summaryCards[3],
            value: data.suspicious_count,
            change: data.total_scans > 0
              ? `${((data.suspicious_count / data.total_scans) * 100).toFixed(1)}% of total`
              : 'No scans yet'
          }
        ];
        this.cdr.detectChanges();
      }
    });

    this.phishingService.getHistory(0, 5).subscribe({
      next: (data) => {
        this.recentScans = data.items.map((item: any) => ({
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
        }));
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });

    this.phishingService.getActivity(7).subscribe({
      next: (data) => {
        this.activityDays = data.days || [];
        this.activityMax = data.max_daily || 1;
        this.activityLoaded = true;
        this.cdr.detectChanges();
      },
      error: () => {
        this.activityLoaded = true;
        this.cdr.detectChanges();
      }
    });
  }

  submitUrl() {
    if (!this.urlToAnalyze || this.urlToAnalyze.trim() === '') {
      this.analysisError = 'Please enter a URL to analyze.';
      this.cdr.detectChanges();
      return;
    }

    let url = this.urlToAnalyze.trim();

    // Length check
    if (url.length > 2048) {
      this.analysisError = 'URL is too long (max 2048 characters).';
      this.cdr.detectChanges();
      return;
    }

    // Auto-prepend https:// if no protocol
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }

    // Basic URL format validation
    try {
      const parsed = new URL(url);
      if (!parsed.hostname || !parsed.hostname.includes('.')) {
        // Allow IP addresses too
        if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(parsed.hostname)) {
          this.analysisError = 'Please enter a valid URL (e.g. google.com or 192.168.1.1).';
          this.cdr.detectChanges();
          return;
        }
      }
    } catch {
      this.analysisError = 'Invalid URL format. Please enter a valid web address.';
      this.cdr.detectChanges();
      return;
    }

    this.isAnalyzing = true;
    this.analysisError = null;
    this.analysisResult = null;
    this.cdr.detectChanges();

    this.phishingService.analyzeUrl({ url: url }).subscribe({
      next: (response) => {
        this.analysisResult = response;
        this.isAnalyzing = false;
        this.urlToAnalyze = '';
        this.loadDashboardData();
        this.cdr.detectChanges();
      },
      error: (err) => {
        // Extract validation error from FastAPI 422 response
        if (err.status === 422 && err.error?.detail) {
          const detail = err.error.detail;
          if (Array.isArray(detail)) {
            this.analysisError = detail.map((d: any) => d.msg).join('. ');
          } else {
            this.analysisError = String(detail);
          }
        } else {
          this.analysisError = 'Failed to analyze URL. Please check the backend connection.';
        }
        this.isAnalyzing = false;
        this.cdr.detectChanges();
      }
    });
  }

  /** Format a date as relative time (e.g. "2 min ago", "1h ago") */
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

  /** Get bar height as a percentage for the activity chart */
  getBarHeight(total: number): number {
    if (this.activityMax === 0) return 0;
    return Math.max(4, (total / this.activityMax) * 100); // min 4% so empty days still have a sliver
  }

  /** Get day-of-week label from a date string */
  getDayLabel(dateStr: string): string {
    const date = new Date(dateStr + 'T12:00:00');
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  }

  summaryCards = [
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
  ];

  recentScans: any[] = [];

  /**
   * Converts a SHAP value into a percentage width for the bar chart.
   * Normalizes against the max absolute SHAP value in the current result.
   */
  getShapBarWidth(shapValue: number): number {
    if (!this.analysisResult?.shap_explanation?.shap_values?.length) return 0;
    const maxAbs = Math.max(
      ...this.analysisResult.shap_explanation.shap_values.map((s: any) => Math.abs(s.shap_value))
    );
    if (maxAbs === 0) return 0;
    return (Math.abs(shapValue) / maxAbs) * 45;
  }
}
