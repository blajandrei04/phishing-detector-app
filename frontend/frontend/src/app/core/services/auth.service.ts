import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, LoginCredentials, RegisterCredentials, ForgotPasswordCredentials } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiBaseUrl}/api/auth`;

  login(credentials: LoginCredentials): Observable<User> {
    return this.http.post<{access_token: string, token_type: string}>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap(tokenData => {
           if (typeof window !== 'undefined') {
              sessionStorage.setItem('token', tokenData.access_token);
           }
        }),
        // fetch current user profile
        switchMap(() => this.getMe())
      );
  }

  getMe(): Observable<User> {
      return this.http.get<User>(`${this.apiUrl}/me`);
  }

  register(credentials: RegisterCredentials): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/register`, credentials);
  }

  forgotPassword(credentials: ForgotPasswordCredentials): Observable<{message: string, reset_token: string | null}> {
    return this.http.post<{message: string, reset_token: string | null}>(`${this.apiUrl}/forgot-password`, credentials);
  }

  resetPassword(token: string, newPassword: string): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/reset-password`, {
      token,
      new_password: newPassword
    });
  }

  updateProfile(data: { email?: string; username?: string }): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/me`, data);
  }

  changePassword(currentPassword: string, newPassword: string): Observable<{message: string}> {
    return this.http.put<{message: string}>(`${this.apiUrl}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  logout(): Observable<boolean> {
    return new Observable<boolean>(observer => {
        if (typeof window !== 'undefined') {
            sessionStorage.removeItem('token');
        }
        observer.next(true);
        observer.complete();
    });
  }
}

