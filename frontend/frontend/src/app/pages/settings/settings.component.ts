import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { AuthFacade } from '../../core/facades/auth.facade';
import { User } from '../../models/auth.models';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.html',
  styleUrl: './settings.scss',
})
export class SettingsComponent implements OnInit {
  private authService = inject(AuthService);
  authFacade = inject(AuthFacade);

  // Profile
  user: User | null = null;
  profileUsername = '';
  profileEmail = '';
  profileSaving = false;
  profileMessage = '';
  profileError = '';

  // Password
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  passwordSaving = false;
  passwordMessage = '';
  passwordError = '';

  // Account info
  memberSince = '';

  ngOnInit(): void {
    this.authFacade.user$.subscribe(user => {
      if (user) {
        this.user = user;
        this.profileUsername = user.username;
        this.profileEmail = user.email;
      }
    });
  }

  saveProfile(): void {
    this.profileMessage = '';
    this.profileError = '';

    if (!this.profileUsername.trim() || !this.profileEmail.trim()) {
      this.profileError = 'Username and email are required.';
      return;
    }

    this.profileSaving = true;
    this.authService.updateProfile({
      username: this.profileUsername,
      email: this.profileEmail
    }).subscribe({
      next: (updatedUser) => {
        this.profileSaving = false;
        this.profileMessage = 'Profile updated successfully!';
        // Re-login to refresh the token with the new username
        this.user = updatedUser;
        setTimeout(() => this.profileMessage = '', 4000);
      },
      error: (err) => {
        this.profileSaving = false;
        this.profileError = err.error?.detail || 'Failed to update profile.';
      }
    });
  }

  changePassword(): void {
    this.passwordMessage = '';
    this.passwordError = '';

    if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
      this.passwordError = 'All password fields are required.';
      return;
    }

    if (this.newPassword.length < 6) {
      this.passwordError = 'New password must be at least 6 characters.';
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.passwordError = 'New passwords do not match.';
      return;
    }

    this.passwordSaving = true;
    this.authService.changePassword(this.currentPassword, this.newPassword).subscribe({
      next: () => {
        this.passwordSaving = false;
        this.passwordMessage = 'Password changed successfully!';
        this.currentPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
        setTimeout(() => this.passwordMessage = '', 4000);
      },
      error: (err) => {
        this.passwordSaving = false;
        this.passwordError = err.error?.detail || 'Failed to change password.';
      }
    });
  }
}
