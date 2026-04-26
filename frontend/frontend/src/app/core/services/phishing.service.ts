import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';
import { AnalyzeRequest } from '../../models/analyze-request.model';
import { AnalyzeResponse } from '../../models/analyze-response.model';

@Injectable({
  providedIn: 'root'
})
export class PhishingService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiBaseUrl}/api`;

  analyzeUrl(request: AnalyzeRequest): Observable<AnalyzeResponse> {
    return this.http.post<AnalyzeResponse>(`${this.apiUrl}/analyze`, request);
  }

  getStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/stats`);
  }

  getHistory(skip: number = 0, limit: number = 10, verdict: string = '', search: string = ''): Observable<any> {
    let url = `${this.apiUrl}/history?skip=${skip}&limit=${limit}`;
    if (verdict && verdict !== 'all') {
      url += `&verdict=${verdict}`;
    }
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }
    return this.http.get(url);
  }

  getActivity(days: number = 7): Observable<any> {
    return this.http.get(`${this.apiUrl}/stats/activity?days=${days}`);
  }

  submitFeedback(payload: { url: string, original_verdict: string, user_reported_verdict: string, comments?: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/feedback`, payload);
  }
}
