from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from stages import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/admin/'), name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^data-import/', include('tabimport.urls')),

    url(r'^attribution/$', views.AttributionView.as_view(), name='attribution'),
    url(r'^stages/export/(?P<scope>all)?/?$', views.stages_export, name='stages_export'),

    url(r'^institutions/$', views.CorporationListView.as_view(), name='corporations'),
    url(r'^institutions/(?P<pk>\d+)/$', views.CorporationView.as_view(), name='corporation'),

    # AJAX/JSON urls
    url(r'^section/(?P<pk>\d+)/periods/', views.section_periods),
    url(r'^section/(?P<pk>\d+)/classes/', views.section_classes),
    url(r'^period/(?P<pk>\d+)/students/', views.period_students),
    url(r'^period/(?P<pk>\d+)/corporations/', views.period_availabilities),
    # Training params in POST:
    url(r'^training/new/', views.new_training, name="new_training"),
    url(r'^training/del/', views.del_training, name="del_training"),
    url(r'^training/by_period/(?P<pk>\d+)/', views.TrainingsByPeriodView.as_view()),

    url(r'^student/(?P<pk>\d+)/summary/', views.StudentSummaryView.as_view()),
    url(r'^availability/(?P<pk>\d+)/summary/', views.AvailabilitySummaryView.as_view()),
    url(r'^corporation/(?P<pk>\d+)/contacts/', views.CorpContactJSONView.as_view()),
]
