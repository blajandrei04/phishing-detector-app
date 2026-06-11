import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthFacade } from '../../core/facades/auth.facade';
import { AuthService } from '../../core/services/auth.service';
import { Store } from '@ngrx/store';
import * as AuthActions from '../../core/store/auth/auth.actions';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  public authFacade = inject(AuthFacade);
  public authService = inject(AuthService);
  private store = inject(Store);

  mode = signal<'login' | 'register' | 'forgot' | 'reset'>('login');
  showPassword = signal(false);
  showRegPassword = signal(false);
  showResetPassword = signal(false);
  showResetConfirmPassword = signal(false);
  message = signal('');
  resetToken = '';

  loginForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(4)]]
  });

  registerForm: FormGroup = this.fb.group({
    firstName: ['', Validators.required],
    lastName: ['', Validators.required],
    organization: [''],
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  forgotForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]]
  });

  resetForm: FormGroup = this.fb.group({
    new_password: ['', [Validators.required, Validators.minLength(6)]],
    confirm_password: ['', [Validators.required]]
  });

  setMode(newMode: 'login' | 'register' | 'forgot' | 'reset'): void {
    this.mode.set(newMode);
    this.message.set('');
    // Clear stale auth store errors when switching modes
    this.store.dispatch(AuthActions.loginFailure({ error: '' }));
  }

  togglePassword(field: 'login' | 'register' | 'reset' | 'resetConfirm'): void {
    switch (field) {
      case 'login':
        this.showPassword.update(v => !v);
        break;
      case 'register':
        this.showRegPassword.update(v => !v);
        break;
      case 'reset':
        this.showResetPassword.update(v => !v);
        break;
      case 'resetConfirm':
        this.showResetConfirmPassword.update(v => !v);
        break;
    }
  }

  onSubmit(): void {
    const currentMode = this.mode();

    if (currentMode === 'login' && this.loginForm.valid) {
      this.authFacade.login(this.loginForm.value);
    } 
    else if (currentMode === 'register' && this.registerForm.valid) {
      this.authService.register(this.registerForm.value).subscribe({
        next: () => {
          this.message.set('Registration successful! Please login.');
          this.setMode('login');
        },
        error: (err) => {
          this.message.set(this.humanizeError(err, 'Registration failed. Please try again.'));
        }
      });
    }
    else if (currentMode === 'forgot' && this.forgotForm.valid) {
      this.authService.forgotPassword(this.forgotForm.value).subscribe({
        next: (res) => {
          if (res.reset_token) {
            // Token received — transition to reset form
            this.resetToken = res.reset_token;
            this.message.set('');
            this.setMode('reset');
            this.message.set('Token verified! Enter your new password below.');
          } else {
            this.message.set(res.message);
          }
        },
        error: () => {
          this.message.set('Request failed. Please try again.');
        }
      });
    }
    else if (currentMode === 'reset' && this.resetForm.valid) {
      const { new_password, confirm_password } = this.resetForm.value;
      if (new_password !== confirm_password) {
        this.message.set('Passwords do not match.');
        return;
      }
      this.authService.resetPassword(this.resetToken, new_password).subscribe({
        next: () => {
          this.message.set('Password reset successful! You can now login.');
          this.resetToken = '';
          this.setMode('login');
        },
        error: (err) => {
          this.message.set(err.error?.detail || 'Reset failed. Token may have expired.');
        }
      });
    }
    else {
      if (currentMode === 'login') this.loginForm.markAllAsTouched();
      if (currentMode === 'register') this.registerForm.markAllAsTouched();
      if (currentMode === 'forgot') this.forgotForm.markAllAsTouched();
      if (currentMode === 'reset') this.resetForm.markAllAsTouched();
    }
  }

  /**
   * Extracts a human-readable error message from various backend response formats.
   */
  private humanizeError(err: any, fallback: string): string {
    const detail = err?.error?.detail;

    // String detail from backend (e.g., "Username already taken")
    if (detail && typeof detail === 'string') {
      return detail;
    }

    // FastAPI validation error array [{msg, loc, type}]
    if (Array.isArray(detail)) {
      return detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join('. ');
    }

    // Object with a message property
    if (detail && typeof detail === 'object' && detail.message) {
      return detail.message;
    }

    // Generic error message from Error object
    if (err?.error?.message && typeof err.error.message === 'string') {
      return err.error.message;
    }

    // HTTP status-based fallbacks
    const status = err?.status;
    if (status === 409) return 'An account with these credentials already exists.';
    if (status === 422) return 'Please check your input and try again.';
    if (status === 0) return 'Unable to reach the server. Please check your connection.';

    return fallback;
  }
}
