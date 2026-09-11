"""
URL configuration for centro_comando project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API REST (JSON). Va antes que el include de la raíz para que el
    # prefijo 'api/' no lo capture el enrutado de las vistas HTML.
    path('api/', include('infraestructura.api_urls')),
    # Login/logout de la API navegable de DRF: permite autenticarse desde
    # el navegador y probar POST/PUT/DELETE, que con IsAuthenticatedOrReadOnly
    # están cerrados a usuarios anónimos.
    path('api-auth/', include('rest_framework.urls')),

    # Documentación de la API: el schema en sí (YAML/JSON) más las dos
    # interfaces que lo consumen. Se separan porque cada una la usa un
    # público distinto: Swagger UI para probar peticiones en vivo, Redoc
    # para lectura de referencia.
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("",include('infraestructura.urls')),
]
