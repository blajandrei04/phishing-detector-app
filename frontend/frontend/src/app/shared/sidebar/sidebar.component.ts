import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthFacade } from '../../core/facades/auth.facade';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
})
export class SidebarComponent {
  authFacade = inject(AuthFacade);

  onLogout(): void {
    this.authFacade.logout();
  }
}
