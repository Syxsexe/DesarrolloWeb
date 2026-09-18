import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, map, shareReplay, tap } from 'rxjs';

import type { components } from '../api/schema';

type TokenObtainPair = components['schemas']['TokenObtainPair'];
type TokenRefresh = components['schemas']['TokenRefresh'];

const ACCESS_KEY = 'access';
const REFRESH_KEY = 'refresh';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly accessToken = signal<string | null>(localStorage.getItem(ACCESS_KEY));
  private readonly refreshToken = signal<string | null>(localStorage.getItem(REFRESH_KEY));

  readonly isAuthenticated = computed(() => this.accessToken() !== null);

  private refreshInFlight$: Observable<string> | null = null;

  getAccessToken(): string | null {
    return this.accessToken();
  }

  getRefreshToken(): string | null {
    return this.refreshToken();
  }

  login(username: string, password: string) {
    return this.http.post<TokenObtainPair>('/api/token/', { username, password }).pipe(
      tap(({ access, refresh }) => this.setTokens(access, refresh)),
    );
  }

  logout(): void {
    this.accessToken.set(null);
    this.refreshToken.set(null);
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  /**
   * Refresca el access token. Comparte el observable en curso entre llamadas
   * concurrentes (varias peticiones fallando a la vez por access expirado)
   * para no disparar múltiples POST /api/token/refresh/ simultáneos.
   */
  refreshAccessToken(): Observable<string> {
    if (this.refreshInFlight$) {
      return this.refreshInFlight$;
    }

    const refresh = this.refreshToken();
    if (!refresh) {
      throw new Error('No hay refresh token disponible.');
    }

    this.refreshInFlight$ = this.http.post<TokenRefresh>('/api/token/refresh/', { refresh }).pipe(
      tap({
        next: ({ access }) => {
          this.accessToken.set(access);
          localStorage.setItem(ACCESS_KEY, access);
        },
        complete: () => (this.refreshInFlight$ = null),
        error: () => (this.refreshInFlight$ = null),
      }),
      map(({ access }) => access),
      shareReplay(1),
    );

    return this.refreshInFlight$;
  }

  private setTokens(access: string, refresh: string): void {
    this.accessToken.set(access);
    this.refreshToken.set(refresh);
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  }
}
