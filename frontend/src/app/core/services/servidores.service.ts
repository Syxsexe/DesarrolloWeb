import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import type { Paginated } from '../models/paginated.model';
import type { NodoServidor, NodoServidorDetalle, NodoServidorPayload } from '../models/servidor.model';
import type { RegistroAuditoria } from '../models/auditoria.model';
import type { IncidenciaServidor } from '../models/incidencia.model';
import type { MantenimientoNodo } from '../models/mantenimiento.model';

export interface ServidoresListParams {
  search?: string;
  ordering?: string;
  en_produccion?: boolean;
  motor?: string;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class ServidoresService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/servidores/';

  list(params: ServidoresListParams = {}) {
    return this.http.get<Paginated<NodoServidor>>(this.base, { params: toHttpParams(params) });
  }

  get(id: number) {
    return this.http.get<NodoServidorDetalle>(`${this.base}${id}/`);
  }

  create(payload: NodoServidorPayload) {
    return this.http.post<NodoServidor>(this.base, payload);
  }

  update(id: number, payload: Partial<NodoServidorPayload>) {
    return this.http.patch<NodoServidor>(`${this.base}${id}/`, payload);
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}${id}/`);
  }

  // Sub-recursos anidados: la ficha de detalle ya trae auditorías e
  // incidencias en una sola petición (GET /api/servidores/:id/ ->
  // NodoServidorDetalle), así que estos métodos no se usan en ese flujo.
  // Quedan disponibles por si algún listado necesita consultarlos aparte,
  // paginados e independientes del detalle completo del nodo.
  auditorias(id: number) {
    return this.http.get<Paginated<RegistroAuditoria>>(`${this.base}${id}/auditorias/`);
  }

  incidencias(id: number, estado?: string) {
    return this.http.get<Paginated<IncidenciaServidor>>(`${this.base}${id}/incidencias/`, {
      params: toHttpParams({ estado }),
    });
  }

  mantenimientos(id: number, completado?: boolean) {
    return this.http.get<Paginated<MantenimientoNodo>>(`${this.base}${id}/mantenimientos/`, {
      params: toHttpParams({ completado }),
    });
  }
}

export function toHttpParams(params: object): HttpParams {
  let httpParams = new HttpParams();
  Object.entries(params as Record<string, unknown>).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      httpParams = httpParams.set(key, String(value));
    }
  });
  return httpParams;
}
