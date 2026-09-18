from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class SmokeAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('ops', password='clave-de-prueba')

    def test_lectura_anonima(self):
        self.assertEqual(self.client.get('/api/servidores/').status_code, 200)
        self.assertEqual(self.client.get('/api/mantenimientos/').status_code, 200)

    def test_escritura_anonima_rechazada(self):
        r = self.client.post('/api/servidores/', {
            'nombre_host': 'nodo-x', 'direccion_ip': '10.10.0.5'}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_flujo_jwt(self):
        r = self.client.post('/api/token/',
                             {'username': 'ops', 'password': 'clave-de-prueba'},
                             format='json')
        self.assertEqual(r.status_code, 200)
        access = r.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        r = self.client.post('/api/servidores/', {
            'nombre_host': 'nodo-x', 'direccion_ip': '10.10.0.5'}, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        nodo = r.data['id']

        r = self.client.post('/api/mantenimientos/', {
            'servidor': nodo, 'titulo_tarea': 'Parche',
            'descripcion_tecnica': 'kernel', 'tipo': 'seguridad',
            'fecha_programada': '2026-10-01T02:00:00Z'}, format='json')
        self.assertEqual(r.status_code, 201, r.data)

        r = self.client.get(f'/api/servidores/{nodo}/mantenimientos/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_validador_ip_devuelve_error_por_campo(self):
        r = self.client.post('/api/token/',
                             {'username': 'ops', 'password': 'clave-de-prueba'},
                             format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        r = self.client.post('/api/servidores/', {
            'nombre_host': 'nodo-y', 'direccion_ip': '192.168.1.7'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('direccion_ip', r.data)
