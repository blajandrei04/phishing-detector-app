import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable, shareReplay, tap } from 'rxjs';
import { AnalyzeRequest } from '../../models/analyze-request.model';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Injectable({
  providedIn: 'root'
})
export class PhishingService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiBaseUrl}/api`;

  // RxJS Caches
  private statsCache$: Observable<any> | null = null;
  private activityCache$: Observable<any> | null = null;
  private feedbackCache$: Observable<any[]> | null = null;
  private historyCache = new Map<string, Observable<any>>();

  analyzeUrl(request: AnalyzeRequest): Observable<AnalyzeResponse> {
    return this.http.post<AnalyzeResponse>(`${this.apiUrl}/analyze`, request).pipe(
      tap(() => {
        // Invalidate caches when a new scan occurs
        this.statsCache$ = null;
        this.activityCache$ = null;
        this.historyCache.clear();
      })
    );
  }

  getStats(): Observable<any> {
    if (!this.statsCache$) {
      this.statsCache$ = this.http.get(`${this.apiUrl}/stats`).pipe(
        shareReplay(1)
      );
    }
    return this.statsCache$;
  }

  getHistory(skip: number = 0, limit: number = 10, verdict: string = '', search: string = ''): Observable<any> {
    let url = `${this.apiUrl}/history?skip=${skip}&limit=${limit}`;
    if (verdict && verdict !== 'all') {
      url += `&verdict=${verdict}`;
    }
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }

    // Cache the history based on the full query string
    if (!this.historyCache.has(url)) {
      const request$ = this.http.get(url).pipe(shareReplay(1));
      this.historyCache.set(url, request$);
    }
    
    return this.historyCache.get(url)!;
  }

  getActivity(days: number = 7): Observable<any> {
    const url = `${this.apiUrl}/stats/activity?days=${days}`;
    if (!this.activityCache$) {
       this.activityCache$ = this.http.get(url).pipe(shareReplay(1));
    }
    return this.activityCache$;
  }

  submitFeedback(payload: { url: string, original_verdict: string, user_reported_verdict: string, comments?: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/feedback`, payload).pipe(
      tap(() => {
        this.feedbackCache$ = null; // Invalidate cache
      })
    );
  }

  getFeedback(): Observable<any[]> {
    if (!this.feedbackCache$) {
      this.feedbackCache$ = this.http.get<any[]>(`${this.apiUrl}/feedback`).pipe(
        shareReplay(1)
      );
    }
    return this.feedbackCache$;
  }

  deleteFeedback(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/feedback/${id}`).pipe(
      tap(() => this.feedbackCache$ = null) // Invalidate cache
    );
  }

  acknowledgeFeedback(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/feedback/${id}/acknowledge`, {}).pipe(
      tap(() => {
        this.feedbackCache$ = null;
        // Invalidate history and stats as well, since acknowledging changes the DB dataset
        this.statsCache$ = null;
        this.activityCache$ = null;
      })
    );
  }
  
  clearAllCaches() {
    this.statsCache$ = null;
    this.activityCache$ = null;
    this.feedbackCache$ = null;
    this.historyCache.clear();
  }
}
