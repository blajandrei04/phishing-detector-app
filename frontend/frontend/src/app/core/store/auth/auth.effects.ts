import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { map, mergeMap, catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../../services/auth.service';
import * as AuthActions from './auth.actions';
import { Router } from '@angular/router';

@Injectable()
export class AuthEffects {
  private actions$ = inject(Actions);
  private authService = inject(AuthService);
  private router = inject(Router);

  login$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.login),
      mergeMap(action =>
        this.authService.login(action.credentials).pipe(
          map(user => AuthActions.loginSuccess({ user })),
          catchError(error => {
            const friendlyMessage = this.getHumanizedError(error);
            return of(AuthActions.loginFailure({ error: friendlyMessage }));
          })
        )
      )
    )
  );

  loginSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess),
        map(() => {
          this.router.navigate(['/dashboard']); // Redirect to dashboard explicitly on success
        })
      ),
    { dispatch: false }
  );

  logout$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.logout),
      switchMap(() =>
        this.authService.logout().pipe(
          map(() => {
            this.router.navigate(['/login']);
            return AuthActions.logoutSuccess();
          })
        )
      )
    )
  );

  checkAuth$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.checkAuth),
      switchMap(() => {
        if (typeof window !== 'undefined' && sessionStorage.getItem('token')) {
          return this.authService.getMe().pipe(
            map(user => AuthActions.checkAuthSuccess({ user })),
            catchError(() => of(AuthActions.checkAuthFailure()))
          );
        }
        return of(AuthActions.checkAuthFailure());
      })
    )
  );

  checkAuthSuccessRedirect$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.checkAuthSuccess),
        map(() => {
          if (this.router.url === '/login' || this.router.url === '/') {
            this.router.navigate(['/dashboard']);
          }
        })
      ),
    { dispatch: false }
  );

  /**
   * Converts raw HTTP errors into user-friendly messages.
   */
  private getHumanizedError(error: any): string {
    // Try to extract backend detail message first
    const detail = error?.error?.detail;
    if (detail && typeof detail === 'string') {
      return detail;
    }

    // Map common HTTP status codes to friendly messages
    const status = error?.status;
    switch (status) {
      case 401:
        return 'Invalid username or password. Please try again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'Account not found. Please check your credentials.';
      case 422:
        return 'Please check your credentials and try again.';
      case 429:
        return 'Too many attempts. Please wait a moment and try again.';
      case 500:
        return 'Our servers are having trouble right now. Please try again later.';
      case 0:
        return 'Unable to reach the server. Please check your internet connection.';
      default:
        return 'Something went wrong. Please try again later.';
    }
  }
}
