import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SidebarComponent } from './shared/sidebar/sidebar.component';
import { AuthFacade } from './core/facades/auth.facade';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, SidebarComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss'],
})
export class App implements OnInit {
  public authFacade = inject(AuthFacade);
  protected readonly title = signal('frontend');

  ngOnInit() {
    this.authFacade.checkAuth();
  }
}
