import { Component, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PhishingService } from '../../core/services/phishing.service';
import { UrlValidatorService } from '../../core/services/url-validator.service';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Component({
  selector: 'app-analyzer',
  standalone: true,
  imports: [FormsModule],
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
    @Inject(PLATFORM_ID) private platformId: Object,
    private urlValidator: UrlValidatorService
  ) {}

  submit(): void {
    const validation = this.urlValidator.validate(this.url);
    if (!validation.isValid) {
      this.error = validation.errorMessage || 'Invalid URL';
      return;
    }
    
    let url = validation.formattedUrl;

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
          this.error = Array.isArray(detail)
            ? detail.map((d: any) => d.msg).join('. ')
            : String(detail);
        } else {
          this.error = 'Failed to analyze URL. Check backend and try again.';
        }
      },
    });
  }
}
