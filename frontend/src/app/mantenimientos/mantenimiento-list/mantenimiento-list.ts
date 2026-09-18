import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { MantenimientosService } from '../../core/services/mantenimientos.service';
import type { MantenimientoNodo } from '../../core/models/mantenimiento.model';
import type { Paginated } from '../../core/models/paginated.model';

@Component({
  selector: 'app-mantenimiento-list',
  imports: [RouterLink, DatePipe],
  templateUrl: './mantenimiento-list.html',
})
export class MantenimientoList {
  private readonly mantenimientosService = inject(MantenimientosService);

  protected readonly page = signal<Paginated<MantenimientoNodo> | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal<string | null>(null);

  constructor() {
    this.cargar();
  }

  cargar(url?: string): void {
    this.cargando.set(true);
    this.error.set(null);

    const pageNumber = url ? Number(new URL(url).searchParams.get('page')) : undefined;

    this.mantenimientosService.list(pageNumber ? { page: pageNumber } : {}).subscribe({
      next: (page) => {
        this.page.set(page);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar la agenda de mantenimientos.');
        this.cargando.set(false);
      },
    });
  }
}
