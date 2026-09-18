import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import type { Paginated } from '../models/paginated.model';
import type { MantenimientoNodo, MantenimientoNodoPayload } from '../models/mantenimiento.model';
import { toHttpParams } from './servidores.service';

export interface MantenimientosListParams {
  search?: string;
  ordering?: string;
  servidor?: number;
  tipo?: string;
  completado?: boolean;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class MantenimientosService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/mantenimientos/';

  list(params: MantenimientosListParams = {}) {
    return this.http.get<Paginated<MantenimientoNodo>>(this.base, { params: toHttpParams(params) });
  }

  get(id: number) {
    return this.http.get<MantenimientoNodo>(`${this.base}${id}/`);
  }

  create(payload: MantenimientoNodoPayload) {
    return this.http.post<MantenimientoNodo>(this.base, payload);
  }

  update(id: number, payload: Partial<MantenimientoNodoPayload>) {
    return this.http.patch<MantenimientoNodo>(`${this.base}${id}/`, payload);
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}${id}/`);
  }
}
