import { Component, inject, signal, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PhishingService } from '../../core/services/phishing.service';
import { UrlValidatorService } from '../../core/services/url-validator.service';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Component({
  selector: 'app-analyzer',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './analyzer.component.html',
  styleUrl: './analyzer.component.scss',
})
export class AnalyzerComponent {
  private phishingService = inject(PhishingService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private urlValidator = inject(UrlValidatorService);

  url = signal('');
  loading = signal(false);
  error = signal('');
  howExpanded = signal(false);

  demoUrls = [
    { label: 'Safe — Google', url: 'https://www.google.com', type: 'safe' },
    { label: 'Safe — GitHub', url: 'https://github.com', type: 'safe' },
    { label: 'Phishing — Fake PayPal', url: 'http://login-update-account-paypal.com', type: 'phishing' },
    { label: 'Phishing — IP Login', url: 'http://192.168.1.1/login.php', type: 'phishing' },
    { label: 'Suspicious — Shortener', url: 'http://bit.ly/free-money', type: 'phishing' },
  ];

  fillDemo(demoUrl: string): void {
    this.url.set(demoUrl);
    this.error.set('');
  }

  submit(): void {
    const validation = this.urlValidator.validate(this.url());
    if (!validation.isValid) {
      this.error.set(validation.errorMessage || 'Invalid URL');
      return;
    }
    
    let url = validation.formattedUrl;

    this.loading.set(true);
    this.error.set('');

    this.phishingService.analyzeUrl({ url: url }).subscribe({
      next: (result: AnalyzeResponse) => {
        this.loading.set(false);
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('lastResult', JSON.stringify(result));
        }
        this.router.navigate(['/results']);
      },
      error: (err) => {
        this.loading.set(false);
        if (err.status === 422 && err.error?.detail) {
          const detail = err.error.detail;
          this.error.set(
            Array.isArray(detail)
              ? detail.map((d: any) => d.msg).join('. ')
              : String(detail)
          );
        } else {
          this.error.set('Failed to analyze URL. Check backend and try again.');
        }
      },
    });
  }
}
