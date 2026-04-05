import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.component.html',
  styleUrl: './results.component.scss',
})
export class ResultsComponent implements OnInit {
  result: AnalyzeResponse | null = null;

  ngOnInit(): void {
    const raw = localStorage.getItem('lastResult');
    this.result = raw ? JSON.parse(raw) : null;
  }
}