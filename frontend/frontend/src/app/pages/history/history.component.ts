import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
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
  private cdr = inject(ChangeDetectorRef);

  scans: any[] = [];
  totalScans: number = 0;
  isLoading: boolean = true;
  loadError: string | null = null;
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 10;
  
  // Filters
  searchQuery: string = '';
  selectedVerdict: string = 'all';

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory() {
    this.isLoading = true;
    this.loadError = null;
    const skip = (this.currentPage - 1) * this.pageSize;
    
    this.phishingService.getHistory(skip, this.pageSize, this.selectedVerdict, this.searchQuery)
      .subscribe({
        next: (response) => {
          this.scans = response.items;
          this.totalScans = response.total;
          this.isLoading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error("Failed to fetch history:", err);
          this.loadError = 'Failed to load scan history. Please try again.';
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
  }

  onSearch() {
    this.currentPage = 1; // Reset to first page
    this.loadHistory();
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadHistory();
  }

  nextPage() {
    if (this.currentPage * this.pageSize < this.totalScans) {
      this.currentPage++;
      this.loadHistory();
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadHistory();
    }
  }
  
  get totalPages(): number {
    return Math.ceil(this.totalScans / this.pageSize);
  }
}
