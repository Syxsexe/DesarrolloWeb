import type { components } from '../api/schema';

export type IncidenciaServidor = components['schemas']['IncidenciaServidor'];
export type SeveridadEnum = components['schemas']['SeveridadEnum'];
export type EstadoEnum = components['schemas']['EstadoEnum'];

export type IncidenciaServidorPayload = Pick<
  IncidenciaServidor,
  'servidor' | 'titulo' | 'descripcion' | 'severidad'
>;
