import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map, take } from 'rxjs/operators';
import { AuthFacade } from '../facades/auth.facade';

export const authGuard: CanActivateFn = (route, state) => {
  const authFacade = inject(AuthFacade);
  const router = inject(Router);

  return authFacade.isAuthenticated$.pipe(
    take(1),
    map(isAuthenticated => {
      if (isAuthenticated) {
        return true;
      }
      return router.createUrlTree(['/login']);
    })
  );
};
