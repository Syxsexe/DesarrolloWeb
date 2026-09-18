import type { MotorContenedoresEnum } from './servidor.model';
import type { SeveridadEnum } from './incidencia.model';
import type { TipoEnum } from './mantenimiento.model';

export interface Choice<T extends string> {
  value: T;
  label: string;
}

export const MOTOR_CHOICES: Choice<MotorContenedoresEnum>[] = [
  { value: 'docker', label: 'Docker' },
  { value: 'podman', label: 'Podman' },
  { value: 'lxc', label: 'LXC Linux Containers' },
  { value: 'ninguno', label: 'Sin contenedores' },
];

export const SEVERIDAD_CHOICES: Choice<SeveridadEnum>[] = [
  { value: 'baja', label: 'Baja' },
  { value: 'media', label: 'Media' },
  { value: 'alta', label: 'Alta' },
  { value: 'critica', label: 'Crítica' },
];

export const TIPO_CHOICES: Choice<TipoEnum>[] = [
  { value: 'actualizacion', label: 'Actualización de Sistema' },
  { value: 'backup', label: 'Respaldo de Base de Datos' },
  { value: 'seguridad', label: 'Parche de Seguridad' },
  { value: 'hardware', label: 'Revisión de Hardware' },
];
