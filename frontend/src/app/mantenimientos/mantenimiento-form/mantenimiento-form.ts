import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { MantenimientosService } from '../../core/services/mantenimientos.service';
import { ServidoresService } from '../../core/services/servidores.service';
import { applyBackendErrors } from '../../core/utils/api-error';
import { TIPO_CHOICES } from '../../core/models/choices';
import type { NodoServidor } from '../../core/models/servidor.model';
import type { TipoEnum } from '../../core/models/mantenimiento.model';

/** ISO 8601 del backend -> valor que acepta <input type="datetime-local"> (sin segundos ni zona). */
function isoToDatetimeLocal(iso: string): string {
  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** Valor de <input type="datetime-local"> -> ISO 8601 que espera el backend. */
function datetimeLocalToIso(value: string): string {
  return new Date(value).toISOString();
}

@Component({
  selector: 'app-mantenimiento-form',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './mantenimiento-form.html',
})
export class MantenimientoForm {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly mantenimientosService = inject(MantenimientosService);
  private readonly servidoresService = inject(ServidoresService);

  protected readonly tipoChoices = TIPO_CHOICES;
  protected readonly servidores = signal<NodoServidor[]>([]);
  protected readonly enviando = signal(false);
  protected readonly errorGeneral = signal<string | null>(null);
  protected readonly cargando = signal(false);

  private readonly id = this.route.snapshot.paramMap.get('id');
  protected readonly esEdicion = computed(() => this.id !== null);

  protected readonly form = this.fb.nonNullable.group({
    servidor: [0, [Validators.required, Validators.min(1)]],
    titulo_tarea: ['', Validators.required],
    descripcion_tecnica: ['', Validators.required],
    tipo: this.fb.nonNullable.control<TipoEnum>('actualizacion'),
    fecha_programada: ['', Validators.required],
    completado: [false],
  });

  constructor() {
    // page_size global es 20: si la flota crece más allá de eso, este select
    // dejaría servidores fuera. Documentado como límite conocido; una mejora
    // futura sería paginar el propio <select> o subir el page_size aquí.
    this.servidoresService.list().subscribe((page) => this.servidores.set(page.results));

    if (this.id) {
      this.cargando.set(true);
      this.mantenimientosService.get(Number(this.id)).subscribe({
        next: (m) => {
          this.form.patchValue({
            servidor: m.servidor,
            titulo_tarea: m.titulo_tarea,
            descripcion_tecnica: m.descripcion_tecnica,
            tipo: m.tipo ?? 'actualizacion',
            fecha_programada: isoToDatetimeLocal(m.fecha_programada),
            completado: m.completado ?? false,
          });
          this.cargando.set(false);
        },
        error: () => {
          this.errorGeneral.set('No se pudo cargar el mantenimiento.');
          this.cargando.set(false);
        },
      });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.enviando.set(true);
    this.errorGeneral.set(null);

    const raw = this.form.getRawValue();
    const payload = { ...raw, fecha_programada: datetimeLocalToIso(raw.fecha_programada) };

    const request$ = this.id
      ? this.mantenimientosService.update(Number(this.id), payload)
      : this.mantenimientosService.create(payload);

    request$.subscribe({
      next: (m) => {
        this.enviando.set(false);
        this.router.navigate(['/mantenimientos', m.id]);
      },
      error: (err: HttpErrorResponse) => {
        this.enviando.set(false);
        this.errorGeneral.set(applyBackendErrors(this.form, err));
      },
    });
  }
}
