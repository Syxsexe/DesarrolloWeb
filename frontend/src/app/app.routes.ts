import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () => import('./servidores/servidor-list/servidor-list').then((m) => m.ServidorList),
  },
  {
    path: 'login',
    loadComponent: () => import('./auth/login/login').then((m) => m.Login),
  },

  {
    path: 'servidores/nuevo',
    canActivate: [authGuard],
    loadComponent: () => import('./servidores/servidor-form/servidor-form').then((m) => m.ServidorForm),
  },
  {
    path: 'servidores/:id',
    pathMatch: 'full',
    loadComponent: () => import('./servidores/servidor-detail/servidor-detail').then((m) => m.ServidorDetail),
  },
  {
    path: 'servidores/:id/editar',
    canActivate: [authGuard],
    loadComponent: () => import('./servidores/servidor-form/servidor-form').then((m) => m.ServidorForm),
  },
  {
    path: 'servidores/:id/eliminar',
    canActivate: [authGuard],
    loadComponent: () => import('./servidores/servidor-delete/servidor-delete').then((m) => m.ServidorDelete),
  },
  {
    path: 'servidores/:id/incidencias/nueva',
    canActivate: [authGuard],
    loadComponent: () => import('./incidencias/incidencia-form/incidencia-form').then((m) => m.IncidenciaForm),
  },

  {
    path: 'mantenimientos',
    pathMatch: 'full',
    loadComponent: () =>
      import('./mantenimientos/mantenimiento-list/mantenimiento-list').then((m) => m.MantenimientoList),
  },
  {
    path: 'mantenimientos/nuevo',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./mantenimientos/mantenimiento-form/mantenimiento-form').then((m) => m.MantenimientoForm),
  },
  {
    path: 'mantenimientos/:id',
    pathMatch: 'full',
    loadComponent: () =>
      import('./mantenimientos/mantenimiento-detail/mantenimiento-detail').then((m) => m.MantenimientoDetail),
  },
  {
    path: 'mantenimientos/:id/editar',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./mantenimientos/mantenimiento-form/mantenimiento-form').then((m) => m.MantenimientoForm),
  },
  {
    path: 'mantenimientos/:id/eliminar',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./mantenimientos/mantenimiento-delete/mantenimiento-delete').then((m) => m.MantenimientoDelete),
  },

  { path: '**', redirectTo: '' },
];
