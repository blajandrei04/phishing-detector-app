import { createAction, props } from '@ngrx/store';
import { User, LoginCredentials } from '../../../models/auth.models';

export const login = createAction(
  '[Auth] Login Request',
  props<{ credentials: LoginCredentials }>()
);

export const loginSuccess = createAction(
  '[Auth] Login Success',
  props<{ user: User }>()
);

export const loginFailure = createAction(
  '[Auth] Login Failure',
  props<{ error: string }>()
);

export const logout = createAction('[Auth] Logout');
export const logoutSuccess = createAction('[Auth] Logout Success');
