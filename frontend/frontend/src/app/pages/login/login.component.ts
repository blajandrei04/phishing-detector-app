import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthFacade } from '../../core/facades/auth.facade';
import { AuthService } from '../../core/services/auth.service';

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

  mode: 'login' | 'register' | 'forgot' | 'reset' = 'login';
  message: string = '';
  resetToken: string = '';

  loginForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(4)]]
  });

  registerForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(4)]]
  });

  forgotForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]]
  });

  resetForm: FormGroup = this.fb.group({
    new_password: ['', [Validators.required, Validators.minLength(6)]],
    confirm_password: ['', [Validators.required]]
  });

  setMode(newMode: 'login' | 'register' | 'forgot' | 'reset'): void {
    this.mode = newMode;
    this.message = '';
  }

  onSubmit(): void {
    if (this.mode === 'login' && this.loginForm.valid) {
      this.authFacade.login(this.loginForm.value);
    } 
    else if (this.mode === 'register' && this.registerForm.valid) {
      this.authService.register(this.registerForm.value).subscribe({
        next: () => {
          this.message = 'Registration successful! Please login.';
          this.setMode('login');
        },
        error: (err) => {
          this.message = err.error?.detail || 'Registration failed';
        }
      });
    }
    else if (this.mode === 'forgot' && this.forgotForm.valid) {
      this.authService.forgotPassword(this.forgotForm.value).subscribe({
        next: (res) => {
          if (res.reset_token) {
            // Token received — transition to reset form
            this.resetToken = res.reset_token;
            this.message = '';
            this.setMode('reset');
            this.message = 'Token verified! Enter your new password below.';
          } else {
            this.message = res.message;
          }
        },
        error: () => {
          this.message = 'Request failed. Please try again.';
        }
      });
    }
    else if (this.mode === 'reset' && this.resetForm.valid) {
      const { new_password, confirm_password } = this.resetForm.value;
      if (new_password !== confirm_password) {
        this.message = 'Passwords do not match.';
        return;
      }
      this.authService.resetPassword(this.resetToken, new_password).subscribe({
        next: () => {
          this.message = 'Password reset successful! You can now login.';
          this.resetToken = '';
          this.setMode('login');
        },
        error: (err) => {
          this.message = err.error?.detail || 'Reset failed. Token may have expired.';
        }
      });
    }
    else {
      if (this.mode === 'login') this.loginForm.markAllAsTouched();
      if (this.mode === 'register') this.registerForm.markAllAsTouched();
      if (this.mode === 'forgot') this.forgotForm.markAllAsTouched();
      if (this.mode === 'reset') this.resetForm.markAllAsTouched();
    }
  }
}
