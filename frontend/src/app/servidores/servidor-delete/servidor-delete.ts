import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { ServidoresService } from '../../core/services/servidores.service';
import { ConfirmDelete } from '../../shared/confirm-delete/confirm-delete';
import type { NodoServidorDetalle } from '../../core/models/servidor.model';

@Component({
  selector: 'app-servidor-delete',
  imports: [ConfirmDelete],
  templateUrl: './servidor-delete.html',
})
export class ServidorDelete {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly servidoresService = inject(ServidoresService);

  private readonly id = Number(this.route.snapshot.paramMap.get('id'));

  protected readonly servidor = signal<NodoServidorDetalle | null>(null);
  protected readonly enviando = signal(false);
  protected readonly error = signal<string | null>(null);

  constructor() {
    this.servidoresService.get(this.id).subscribe((nodo) => this.servidor.set(nodo));
  }

  confirmar(): void {
    this.enviando.set(true);
    this.servidoresService.delete(this.id).subscribe({
      next: () => this.router.navigate(['/']),
      error: () => {
        this.enviando.set(false);
        this.error.set('No se pudo eliminar el servidor.');
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/servidores', this.id]);
  }
}
