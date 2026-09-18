import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import type { Paginated } from '../models/paginated.model';
import type { IncidenciaServidor, IncidenciaServidorPayload } from '../models/incidencia.model';
import { toHttpParams } from './servidores.service';

export interface IncidenciasListParams {
  search?: string;
  ordering?: string;
  servidor?: number;
  estado?: string;
  severidad?: string;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class IncidenciasService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/incidencias/';

  list(params: IncidenciasListParams = {}) {
    return this.http.get<Paginated<IncidenciaServidor>>(this.base, { params: toHttpParams(params) });
  }

  get(id: number) {
    return this.http.get<IncidenciaServidor>(`${this.base}${id}/`);
  }

  create(payload: IncidenciaServidorPayload) {
    return this.http.post<IncidenciaServidor>(this.base, payload);
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}${id}/`);
  }

  resolver(id: number) {
    return this.http.post<IncidenciaServidor>(`${this.base}${id}/resolver/`, {});
  }
}
