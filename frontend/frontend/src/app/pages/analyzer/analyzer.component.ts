import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
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
    private router: Router
  ) {}

  submit(): void {
    this.error = '';
    if (!this.url.trim()) {
      this.error = 'Please enter a URL.';
      return;
    }

    this.loading = true;
    this.phishingService.analyzeUrl({ url: this.url.trim() }).subscribe({
      next: (result: AnalyzeResponse) => {
        this.loading = false;
        localStorage.setItem('lastResult', JSON.stringify(result));
        this.router.navigate(['/results']);
      },
      error: () => {
        this.loading = false;
        this.error = 'Failed to analyze URL. Check backend and try again.';
      },
    });
  }
}