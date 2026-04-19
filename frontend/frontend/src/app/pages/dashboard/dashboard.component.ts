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
  
  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
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
            change: data.total_scans > 0 ? `${((data.phishing_count / data.total_scans) * 100).toFixed(1)}% detection rate` : '0% detection'
          },
          {
            ...this.summaryCards[2],
            value: data.legitimate_count,
            change: data.total_scans > 0 ? `${((data.legitimate_count / data.total_scans) * 100).toFixed(1)}% safe rate` : '0% safe'
          },
          {
            ...this.summaryCards[3],
            value: data.total_scans > 0 ? ((data.legitimate_count / data.total_scans) * 100).toFixed(1) + '%' : '0%'
          }
        ];
        this.cdr.detectChanges();
      }
    });

    this.phishingService.getHistory().subscribe({
      next: (data) => {
        this.recentScans = data.items.map((item: any) => ({
          url: item.url,
          risk: item.verdict === 'phishing' ? 'High' : (item.verdict === 'suspicious' ? 'Suspicious' : 'Low'),
          time: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          icon: item.verdict === 'phishing' ? 'bi-x-octagon-fill' : 'bi-check-circle-fill',
          riskColor: item.verdict === 'phishing' ? 'red' : (item.verdict === 'suspicious' ? 'orange' : 'green')
        }));
        this.cdr.detectChanges();
      }
    });
  }

  submitUrl() {
    if (!this.urlToAnalyze || this.urlToAnalyze.trim() === '') return;

    let url = this.urlToAnalyze.trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
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
        this.loadDashboardData(); // Refresh stats fully
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.analysisError = 'Failed to analyze URL. Please check the backend connection.';
        this.isAnalyzing = false;
        this.cdr.detectChanges();
      }
    });
  }

  summaryCards = [
    {
      title: 'Total Scans',
      value: '1,284',
      change: '+12%',
      changeType: 'increase',
      icon: 'bi-shield-check',
      color: 'blue',
    },
    {
      title: 'Threats Detected',
      value: '87',
      change: '6.8% detection rate',
      changeType: 'danger',
      icon: 'bi-shield-exclamation',
      color: 'red',
    },
    {
      title: 'Safe URLs',
      value: '1,197',
      change: '93.2% safe rate',
      changeType: 'increase',
      icon: 'bi-shield-lock',
      color: 'green',
    },
    {
      title: 'Accuracy Rate',
      value: '98.5%',
      change: 'based on verified results',
      changeType: 'neutral',
      icon: 'bi-bullseye',
      color: 'purple',
    },
  ];

  recentScans = [
    {
      url: 'https://example-bank.com',
      risk: 'Low',
      time: '2 minutes ago',
      icon: 'bi-check-circle-fill',
      riskColor: 'green',
    },
    {
      url: 'https://paypal1-login.com',
      risk: 'High',
      time: '15 minutes ago',
      icon: 'bi-exclamation-triangle-fill',
      riskColor: 'red',
    },
    {
      url: 'https://amazon.com',
      risk: 'Low',
      time: '1 hour ago',
      icon: 'bi-check-circle-fill',
      riskColor: 'green',
    },
    {
      url: 'https://secure-verify.com',
      risk: 'Critical',
      time: '2 hours ago',
      icon: 'bi-x-octagon-fill',
      riskColor: 'darkred',
    },
    {
      url: 'https://github.com',
      risk: 'Low',
      time: '3 hours ago',
      icon: 'bi-check-circle-fill',
      riskColor: 'green',
    },
  ];

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
    return (Math.abs(shapValue) / maxAbs) * 45; // 45% max width (half the track)
  }
}
