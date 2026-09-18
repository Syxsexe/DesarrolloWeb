import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { IncidenciasService } from '../../core/services/incidencias.service';
import { ServidoresService } from '../../core/services/servidores.service';
import { applyBackendErrors } from '../../core/utils/api-error';
import { SEVERIDAD_CHOICES } from '../../core/models/choices';
import type { SeveridadEnum } from '../../core/models/incidencia.model';

@Component({
  selector: 'app-incidencia-form',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './incidencia-form.html',
})
export class IncidenciaForm {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly incidenciasService = inject(IncidenciasService);
  private readonly servidoresService = inject(ServidoresService);

  protected readonly severidadChoices = SEVERIDAD_CHOICES;
  protected readonly enviando = signal(false);
  protected readonly errorGeneral = signal<string | null>(null);
  protected readonly hostnameServidor = signal<string | null>(null);

  protected readonly servidorId = Number(this.route.snapshot.paramMap.get('id'));

  protected readonly form = this.fb.nonNullable.group({
    titulo: ['', Validators.required],
    descripcion: ['', Validators.required],
    severidad: this.fb.nonNullable.control<SeveridadEnum>('media'),
  });

  constructor() {
    this.servidoresService.get(this.servidorId).subscribe((nodo) => this.hostnameServidor.set(nodo.nombre_host));
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.enviando.set(true);
    this.errorGeneral.set(null);

    this.incidenciasService
      .create({ ...this.form.getRawValue(), servidor: this.servidorId })
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.router.navigate(['/servidores', this.servidorId]);
        },
        error: (err: HttpErrorResponse) => {
          this.enviando.set(false);
          this.errorGeneral.set(applyBackendErrors(this.form, err));
        },
      });
  }
}
