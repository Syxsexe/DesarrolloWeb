import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ServidoresService } from '../../core/services/servidores.service';
import { IncidenciasService } from '../../core/services/incidencias.service';
import type { NodoServidorDetalle } from '../../core/models/servidor.model';

@Component({
  selector: 'app-servidor-detail',
  imports: [RouterLink, DatePipe],
  templateUrl: './servidor-detail.html',
})
export class ServidorDetail {
  private readonly route = inject(ActivatedRoute);
  private readonly servidoresService = inject(ServidoresService);
  private readonly incidenciasService = inject(IncidenciasService);

  protected readonly servidor = signal<NodoServidorDetalle | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal<string | null>(null);
  protected readonly resolviendoId = signal<number | null>(null);

  private readonly id = Number(this.route.snapshot.paramMap.get('id'));

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.servidoresService.get(this.id).subscribe({
      next: (servidor) => {
        this.servidor.set(servidor);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se encontró el servidor solicitado.');
        this.cargando.set(false);
      },
    });
  }

  resolver(incidenciaId: number): void {
    this.resolviendoId.set(incidenciaId);
    this.incidenciasService.resolver(incidenciaId).subscribe({
      next: () => {
        this.resolviendoId.set(null);
        this.cargar();
      },
      error: (err) => {
        this.resolviendoId.set(null);
        if (err.status === 409) {
          this.error.set('La incidencia ya estaba resuelta.');
        } else {
          this.error.set('No se pudo resolver la incidencia.');
        }
      },
    });
  }
}
