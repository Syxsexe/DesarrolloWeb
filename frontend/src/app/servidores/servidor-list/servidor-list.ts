import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ServidoresService } from '../../core/services/servidores.service';
import type { NodoServidor } from '../../core/models/servidor.model';
import type { Paginated } from '../../core/models/paginated.model';

@Component({
  selector: 'app-servidor-list',
  imports: [RouterLink],
  templateUrl: './servidor-list.html',
})
export class ServidorList {
  private readonly servidoresService = inject(ServidoresService);

  protected readonly page = signal<Paginated<NodoServidor> | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal<string | null>(null);

  constructor() {
    this.cargar();
  }

  cargar(url?: string): void {
    this.cargando.set(true);
    this.error.set(null);

    const pageNumber = url ? Number(new URL(url).searchParams.get('page')) : undefined;

    this.servidoresService.list(pageNumber ? { page: pageNumber } : {}).subscribe({
      next: (page) => {
        this.page.set(page);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar la flota de servidores.');
        this.cargando.set(false);
      },
    });
  }
}
