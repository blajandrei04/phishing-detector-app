import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { delay } from 'rxjs/operators';
import { User, LoginCredentials } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  // Simulating an API call to FastAPI backend
  login(credentials: LoginCredentials): Observable<User> {
    if (credentials.username === 'admin' && credentials.password === 'thesis') {
      return of({
        id: '1',
        username: 'admin',
        role: 'admin',
        token: 'fake-jwt-token-12345'
      }).pipe(delay(800)); // Simulate network latency
    }
    return throwError(() => new Error('Invalid username or password')).pipe(delay(500));
  }

  logout(): Observable<boolean> {
    return of(true).pipe(delay(300));
  }
}
