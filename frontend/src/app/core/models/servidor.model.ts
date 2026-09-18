import type { components } from '../api/schema';

export type NodoServidor = components['schemas']['NodoServidor'];
export type NodoServidorDetalle = components['schemas']['NodoServidorDetalle'];
export type MotorContenedoresEnum = components['schemas']['MotorContenedoresEnum'];

export type NodoServidorPayload = Pick<
  NodoServidor,
  'nombre_host' | 'direccion_ip' | 'motor_contenedores' | 'proxy_inverso' | 'en_produccion'
>;
