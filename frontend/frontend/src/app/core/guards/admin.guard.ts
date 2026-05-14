import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map, take } from 'rxjs/operators';
import { AuthFacade } from '../facades/auth.facade';

export const adminGuard: CanActivateFn = (route, state) => {
  const authFacade = inject(AuthFacade);
  const router = inject(Router);

  return authFacade.user$.pipe(
    take(1),
    map(user => {
      if (user && user.username === 'admin') {
        return true;
      }
      return router.createUrlTree(['/dashboard']);
    })
  );
};
