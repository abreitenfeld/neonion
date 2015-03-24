from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'neonion.views.render_home'),
    url(r'^my_annotations/$', 'neonion.views.my_annotations'),
    url(r'^annotations_occurrences/(?P<quote>.+)$', 'neonion.views.annotations_occurrences'),
    url(r'^ann_documents/(?P<quote>.+)$', 'neonion.views.ann_documents'),
    url(r'^import/$', 'neonion.views.import_document'),
    url(r'^settings/$', 'neonion.views.render_settings'),
    url(r'^query$', 'neonion.views.render_query'),

    url(r'^management/?$', 'neonion.views.accounts_management'),

    url(r'^annotator/(?P<doc_id>.+)$', 'neonion.views.render_annotator'),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^documents/', include('documents.urls')),
    url(r'^endpoint/', include('endpoint.urls')),

    # Elasticsearch proxy
    url(r'^search$', 'neonion.views.resource_search'),

    # Django rest
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)