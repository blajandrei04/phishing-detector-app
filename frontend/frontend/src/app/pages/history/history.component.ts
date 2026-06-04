import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PhishingService } from '../../core/services/phishing.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './history.html',
  styleUrls: ['./history.scss'],
})
export class HistoryComponent implements OnInit {
  private phishingService = inject(PhishingService);
  private router = inject(Router);

  scans = signal<any[]>([]);
  totalScans = signal(0);
  isLoading = signal(true);
  loadError = signal<string | null>(null);
  analyzingUrl = signal<string | null>(null);
  
  // Pagination
  currentPage = signal(1);
  pageSize = 10;
  
  // Filters
  searchQuery = signal('');
  selectedVerdict = signal('all');

  // Derived state
  totalPages = computed(() => Math.ceil(this.totalScans() / this.pageSize));

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory() {
    this.isLoading.set(true);
    this.loadError.set(null);
    const skip = (this.currentPage() - 1) * this.pageSize;
    
    this.phishingService.getHistory(skip, this.pageSize, this.selectedVerdict(), this.searchQuery())
      .subscribe({
        next: (response) => {
          this.scans.set(response.items);
          this.totalScans.set(response.total);
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error("Failed to fetch history:", err);
          this.loadError.set('Failed to load scan history. Please try again.');
          this.isLoading.set(false);
        }
      });
  }

  onSearch() {
    this.currentPage.set(1); // Reset to first page
    this.loadHistory();
  }

  onFilterChange() {
    this.currentPage.set(1);
    this.loadHistory();
  }

  nextPage() {
    if (this.currentPage() * this.pageSize < this.totalScans()) {
      this.currentPage.update(p => p + 1);
      this.loadHistory();
    }
  }

  prevPage() {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
      this.loadHistory();
    }
  }

  viewReport(url: string) {
    this.analyzingUrl.set(url);
    this.phishingService.analyzeUrl({ url }).subscribe({
      next: (response) => {
        localStorage.setItem('lastResult', JSON.stringify(response));
        this.analyzingUrl.set(null);
        this.router.navigate(['/results']);
      },
      error: (err) => {
        console.error("Failed to analyze url:", err);
        this.loadError.set('Failed to load report. Please try again.');
        this.analyzingUrl.set(null);
      }
    });
  }
}
