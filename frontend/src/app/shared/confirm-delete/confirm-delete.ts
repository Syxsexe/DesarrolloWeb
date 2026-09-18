import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-confirm-delete',
  templateUrl: './confirm-delete.html',
})
export class ConfirmDelete {
  readonly titulo = input('¿Estás seguro?');
  readonly mensaje = input.required<string>();
  readonly enviando = input(false);
  readonly error = input<string | null>(null);

  readonly confirm = output<void>();
  readonly cancel = output<void>();
}
