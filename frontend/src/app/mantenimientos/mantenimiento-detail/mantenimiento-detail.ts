import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { MantenimientosService } from '../../core/services/mantenimientos.service';
import type { MantenimientoNodo } from '../../core/models/mantenimiento.model';

@Component({
  selector: 'app-mantenimiento-detail',
  imports: [RouterLink, DatePipe],
  templateUrl: './mantenimiento-detail.html',
})
export class MantenimientoDetail {
  private readonly route = inject(ActivatedRoute);
  private readonly mantenimientosService = inject(MantenimientosService);

  private readonly id = Number(this.route.snapshot.paramMap.get('id'));

  protected readonly mantenimiento = signal<MantenimientoNodo | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal<string | null>(null);

  constructor() {
    this.mantenimientosService.get(this.id).subscribe({
      next: (m) => {
        this.mantenimiento.set(m);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se encontró el mantenimiento solicitado.');
        this.cargando.set(false);
      },
    });
  }
}
