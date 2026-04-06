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
  private apiUrl = `${environment.apiBaseUrl}/api/analyze`;

  analyzeUrl(request: AnalyzeRequest): Observable<AnalyzeResponse> {
    return this.http.post<AnalyzeResponse>(this.apiUrl, request);
  }
}
