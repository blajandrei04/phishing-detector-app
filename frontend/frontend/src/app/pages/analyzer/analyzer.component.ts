import { Component, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PhishingService } from '../../core/services/phishing.service';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Component({
  selector: 'app-analyzer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './analyzer.component.html',
  styleUrl: './analyzer.component.scss',
})
export class AnalyzerComponent {
  url = '';
  loading = false;
  error = '';

  constructor(
    private phishingService: PhishingService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  submit(): void {
    this.error = '';
    if (!this.url.trim()) {
      this.error = 'Please enter a URL.';
      return;
    }

    let url = this.url.trim();

    // Length check
    if (url.length > 2048) {
      this.error = 'URL is too long (max 2048 characters).';
      return;
    }

    // Auto-prepend https://
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }

    // Basic format validation
    try {
      const parsed = new URL(url);
      if (!parsed.hostname || !parsed.hostname.includes('.')) {
        if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(parsed.hostname)) {
          this.error = 'Please enter a valid URL (e.g. google.com).';
          return;
        }
      }
    } catch {
      this.error = 'Invalid URL format. Please enter a valid web address.';
      return;
    }

    this.loading = true;
    this.phishingService.analyzeUrl({ url: url }).subscribe({
      next: (result: AnalyzeResponse) => {
        this.loading = false;
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('lastResult', JSON.stringify(result));
        }
        this.router.navigate(['/results']);
      },
      error: (err) => {
        this.loading = false;
        if (err.status === 422 && err.error?.detail) {
          const detail = err.error.detail;
          this.error = Array.isArray(detail) ? detail.map((d: any) => d.msg).join('. ') : String(detail);
        } else {
          this.error = 'Failed to analyze URL. Check backend and try again.';
        }
      },
    });
  }
}