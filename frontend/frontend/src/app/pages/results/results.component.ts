import { Component, OnInit, PLATFORM_ID, Inject, inject, AfterViewInit, ChangeDetectorRef, NgZone } from '@angular/core';
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
export class ResultsComponent implements OnInit, AfterViewInit {
  result: AnalyzeResponse | null = null;
  isBrowser = false;

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  private phishingService = inject(PhishingService);

  isReporting = false;
  reportSuccess = false;
  reportError = '';

  // Animated score counter
  displayScore = 0;
  displayConfidence = 0;
  scoreAnimationDone = false;
  barConfidence = 0; // to animate the progress bar width smoothly

  // Gauge chart
  gaugeRotation = -90; // starts at left (empty)
  gaugeColor = '#22c55e';

  // Tooltip
  showVerdictTooltip = false;

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.isBrowser = true;
      const raw = localStorage.getItem('lastResult');
      this.result = raw ? JSON.parse(raw) : null;
      this.cdr.detectChanges();
    }
  }

  ngAfterViewInit(): void {
    if (this.result && isPlatformBrowser(this.platformId)) {
      this.animateScore();
      this.animateGauge();
    }
  }

  private animateScore(): void {
    if (!this.result) return;
    const targetScore = Math.round(this.result.score * 1000) / 10;
    const targetConfidence = Math.round(this.result.confidence * 1000) / 10;
    const duration = 1200;
    const startTime = performance.now();

    // Trigger the progress bar transition
    setTimeout(() => {
      this.barConfidence = targetConfidence;
      this.cdr.detectChanges();
    }, 50);

    // Run text counter animation outside Angular zone for high performance
    this.ngZone.runOutsideAngular(() => {
      const animate = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);

        this.displayScore = Math.round(eased * targetScore * 10) / 10;
        this.displayConfidence = Math.round(eased * targetConfidence * 10) / 10;
        this.cdr.detectChanges();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          this.displayScore = targetScore;
          this.displayConfidence = targetConfidence;
          this.scoreAnimationDone = true;
          this.cdr.detectChanges();
        }
      };
      requestAnimationFrame(animate);
    });
  }

  private animateGauge(): void {
    if (!this.result) return;
    const score = this.result.score;
    // Map score [0, 1] to rotation [-90, 90] degrees (half circle)
    const targetRotation = -90 + (score * 180);

    // Set color based on score
    if (score >= 0.7) {
      this.gaugeColor = '#ef4444';
    } else if (score >= 0.4) {
      this.gaugeColor = '#f59e0b';
    } else {
      this.gaugeColor = '#22c55e';
    }

    // Delay setting the rotation slightly so that the browser registers the initial rotation state (-90deg)
    // and triggers a smooth CSS transition.
    setTimeout(() => {
      this.gaugeRotation = targetRotation;
      this.cdr.detectChanges();
    }, 50);
  }

  getGradientBarStyle(): { [key: string]: string } {
    if (!this.result) return {};
    const score = this.result.score;
    // Interpolate between green→yellow→red
    if (score < 0.5) {
      const t = score / 0.5;
      return {
        background: `linear-gradient(90deg, #22c55e ${(1 - t) * 100}%, #f59e0b ${t * 100}%)`,
        height: '6px',
        width: '100%',
        'border-radius': '0 0 16px 16px'
      };
    } else {
      const t = (score - 0.5) / 0.5;
      return {
        background: `linear-gradient(90deg, #f59e0b ${(1 - t) * 100}%, #ef4444 ${t * 100}%)`,
        height: '6px',
        width: '100%',
        'border-radius': '0 0 16px 16px'
      };
    }
  }

  getVerdictExplanation(): string {
    if (!this.result) return '';
    switch (this.result.verdict) {
      case 'phishing':
        return 'The ML model found strong phishing indicators in this URL. It closely matches patterns commonly seen in known phishing websites. Avoid visiting this page.';
      case 'suspicious':
        return 'This URL has some characteristics that could indicate phishing, but the model is not fully confident. Exercise caution and verify the source before interacting.';
      case 'legitimate':
        return 'The URL appears safe based on the features analyzed. It does not match common phishing patterns. However, always stay vigilant online.';
      default:
        return '';
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

  isYoungDomain(): boolean {
    const age = this.result?.dynamic_checks?.domain_age?.domain_age_days;
    return age !== null && age !== undefined && age < 30;
  }
}