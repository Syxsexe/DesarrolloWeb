import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { MantenimientosService } from '../../core/services/mantenimientos.service';
import { ConfirmDelete } from '../../shared/confirm-delete/confirm-delete';
import type { MantenimientoNodo } from '../../core/models/mantenimiento.model';

@Component({
  selector: 'app-mantenimiento-delete',
  imports: [ConfirmDelete],
  templateUrl: './mantenimiento-delete.html',
})
export class MantenimientoDelete {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly mantenimientosService = inject(MantenimientosService);

  private readonly id = Number(this.route.snapshot.paramMap.get('id'));

  protected readonly mantenimiento = signal<MantenimientoNodo | null>(null);
  protected readonly enviando = signal(false);
  protected readonly error = signal<string | null>(null);

  constructor() {
    this.mantenimientosService.get(this.id).subscribe((m) => this.mantenimiento.set(m));
  }

  confirmar(): void {
    this.enviando.set(true);
    this.mantenimientosService.delete(this.id).subscribe({
      next: () => this.router.navigate(['/mantenimientos']),
      error: () => {
        this.enviando.set(false);
        this.error.set('No se pudo eliminar el mantenimiento.');
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/mantenimientos', this.id]);
  }
}
