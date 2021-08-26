"""foodplan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function viewsweek_menu/
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf.urls import url

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import logout_then_login
from cuisine import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.index_page, name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('week_menu/', views.show_next_week_menu, name='week_menu'),
    path('daily_menu/', views.show_daily_menu, name='daily_menu'),
    path('calculator/', views.calculate_products, name='calculator'),
    path('recipe/<int:recipe_id>', views.view_recipe, name='recipe'),
    path('__debug__/', include(debug_toolbar.urls)),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', LoginView.as_view(template_name='registration/login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    url(r'^$', views.dashboard, name='dashboard'),
]

urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
