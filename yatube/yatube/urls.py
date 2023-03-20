
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
]

handler404 = 'core.views.page_not_found'  # обработчик ошибки 404
handler403 = 'core.views.csrf_failure'  # обработчик ошибки 403


# Разрешение брать картинки пользователя в режиме отладки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include('debug_toolbar.urls')),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
