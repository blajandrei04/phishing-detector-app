import { Injectable, inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import { User, LoginCredentials } from '../../models/auth.models';
import * as AuthActions from '../store/auth/auth.actions';
import * as AuthSelectors from '../store/auth/auth.selectors';

@Injectable({
  providedIn: 'root'
})
export class AuthFacade {
  private store = inject(Store);

  user$: Observable<User | null> = this.store.select(AuthSelectors.selectUser);
  isAuthenticated$: Observable<boolean> = this.store.select(AuthSelectors.selectIsAuthenticated);
  isLoading$: Observable<boolean> = this.store.select(AuthSelectors.selectAuthLoading);
  error$: Observable<string | null> = this.store.select(AuthSelectors.selectAuthError);

  login(credentials: LoginCredentials): void {
    this.store.dispatch(AuthActions.login({ credentials }));
  }

  logout(): void {
    this.store.dispatch(AuthActions.logout());
  }
}
