import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

const TOKEN_URLS = ['/api/token/', '/api/token/refresh/'];

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const isTokenRequest = TOKEN_URLS.some((url) => req.url.includes(url));
  const access = auth.getAccessToken();

  const authReq = access && !isTokenRequest
    ? req.clone({ setHeaders: { Authorization: `Bearer ${access}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: unknown) => {
      if (
        error instanceof HttpErrorResponse &&
        error.status === 401 &&
        !isTokenRequest &&
        auth.getRefreshToken()
      ) {
        return auth.refreshAccessToken().pipe(
          switchMap((newAccess) => {
            const retried = req.clone({ setHeaders: { Authorization: `Bearer ${newAccess}` } });
            return next(retried);
          }),
          catchError((refreshError) => {
            auth.logout();
            router.navigate(['/login']);
            return throwError(() => refreshError);
          }),
        );
      }

      return throwError(() => error);
    }),
  );
};
