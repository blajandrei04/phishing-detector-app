import { createReducer, on } from '@ngrx/store';
import { User } from '../../../models/auth.models';
import * as AuthActions from './auth.actions';

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};

export const authReducer = createReducer(
  initialState,
  on(AuthActions.login, state => ({
    ...state,
    isLoading: true,
    error: null
  })),
  on(AuthActions.loginSuccess, (state, { user }) => ({
    ...state,
    isLoading: false,
    isAuthenticated: true,
    user
  })),
  on(AuthActions.loginFailure, (state, { error }) => ({
    ...state,
    isLoading: false,
    error
  })),
  on(AuthActions.logoutSuccess, () => initialState),
  on(AuthActions.checkAuth, state => ({
    ...state,
    isLoading: true
  })),
  on(AuthActions.checkAuthSuccess, (state, { user }) => ({
    ...state,
    isLoading: false,
    isAuthenticated: true,
    user
  })),
  on(AuthActions.checkAuthFailure, state => ({
    ...state,
    isLoading: false,
    isAuthenticated: false,
    user: null
  }))
);
