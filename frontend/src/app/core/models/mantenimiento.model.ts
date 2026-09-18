import type { components } from '../api/schema';

export type MantenimientoNodo = components['schemas']['MantenimientoNodo'];
export type TipoEnum = components['schemas']['TipoEnum'];

export type MantenimientoNodoPayload = Pick<
  MantenimientoNodo,
  'servidor' | 'titulo_tarea' | 'descripcion_tecnica' | 'tipo' | 'completado' | 'fecha_programada'
>;
