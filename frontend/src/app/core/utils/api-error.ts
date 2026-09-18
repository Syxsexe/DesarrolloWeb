import { HttpErrorResponse } from '@angular/common/http';
import { FormGroup } from '@angular/forms';

/**
 * Aplica los errores 400 de DRF ({campo: [mensajes]}) a los controles de un
 * reactive form. Los errores sin campo correspondiente (o el detail de un
 * 401/404/500) se devuelven como string para mostrarlos en una alerta general.
 */
export function applyBackendErrors(form: FormGroup, error: HttpErrorResponse): string | null {
  if (error.status !== 400 || !error.error || typeof error.error !== 'object') {
    return error.error?.detail ?? 'Ocurrió un error inesperado. Inténtalo de nuevo.';
  }

  let generalError: string | null = null;

  Object.entries(error.error as Record<string, unknown>).forEach(([field, messages]) => {
    const texto = Array.isArray(messages) ? messages.join(' ') : String(messages);
    const control = form.get(field);
    if (control) {
      control.setErrors({ backend: texto });
    } else {
      generalError = generalError ? `${generalError} ${texto}` : texto;
    }
  });

  return generalError;
}
