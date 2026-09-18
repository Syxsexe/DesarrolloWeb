import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { ServidoresService } from '../../core/services/servidores.service';
import { applyBackendErrors } from '../../core/utils/api-error';
import { MOTOR_CHOICES } from '../../core/models/choices';
import type { MotorContenedoresEnum } from '../../core/models/servidor.model';

@Component({
  selector: 'app-servidor-form',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './servidor-form.html',
})
export class ServidorForm {
  private readonly fb = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly servidoresService = inject(ServidoresService);

  protected readonly motorChoices = MOTOR_CHOICES;
  protected readonly enviando = signal(false);
  protected readonly errorGeneral = signal<string | null>(null);
  protected readonly cargando = signal(false);

  private readonly id = this.route.snapshot.paramMap.get('id');
  protected readonly esEdicion = computed(() => this.id !== null);

  protected readonly form = this.fb.nonNullable.group({
    nombre_host: ['', [Validators.required, Validators.maxLength(100)]],
    direccion_ip: ['', Validators.required],
    motor_contenedores: this.fb.nonNullable.control<MotorContenedoresEnum>('podman'),
    proxy_inverso: [true],
    en_produccion: [true],
  });

  constructor() {
    if (this.id) {
      this.cargando.set(true);
      this.servidoresService.get(Number(this.id)).subscribe({
        next: (nodo) => {
          this.form.patchValue({
            nombre_host: nodo.nombre_host,
            direccion_ip: nodo.direccion_ip,
            motor_contenedores: nodo.motor_contenedores ?? 'podman',
            proxy_inverso: nodo.proxy_inverso ?? true,
            en_produccion: nodo.en_produccion ?? true,
          });
          this.cargando.set(false);
        },
        error: () => {
          this.errorGeneral.set('No se pudo cargar el servidor.');
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
    const payload = this.form.getRawValue();

    const request$ = this.id
      ? this.servidoresService.update(Number(this.id), payload)
      : this.servidoresService.create(payload);

    request$.subscribe({
      next: (nodo) => {
        this.enviando.set(false);
        this.router.navigate(['/servidores', nodo.id]);
      },
      error: (err: HttpErrorResponse) => {
        this.enviando.set(false);
        this.errorGeneral.set(applyBackendErrors(this.form, err));
      },
    });
  }
}
