import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import type { Paginated } from '../models/paginated.model';
import type { RegistroAuditoria } from '../models/auditoria.model';
import { toHttpParams } from './servidores.service';

export interface AuditoriasListParams {
  search?: string;
  ordering?: string;
  servidor?: number;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class AuditoriasService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/auditorias/';

  list(params: AuditoriasListParams = {}) {
    return this.http.get<Paginated<RegistroAuditoria>>(this.base, { params: toHttpParams(params) });
  }

  get(id: number) {
    return this.http.get<RegistroAuditoria>(`${this.base}${id}/`);
  }
}
