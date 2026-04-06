import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
})
export class DashboardComponent {
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
}
