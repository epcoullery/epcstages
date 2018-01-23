from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from stages import views
from candidats import views as candidats_views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/admin/', permanent=True), name='home'),

    url(r'^admin/', admin.site.urls),
    url(r'^admin/(?P<pk>\d+)/convocation/', candidats_views.SendConvocationView.as_view(), name='send-convocation'),
    url(r'^import_students/', views.StudentImportView.as_view(), name='import-students'),
    url(r'^import_hp/', views.HPImportView.as_view(), name='import-hp'),
    url(r'^import_hp_contacts/', views.HPContactsImportView.as_view(), name='import-hp-contacts'),
    url(r'^import_bulletins/', views.ImportBulletinView.as_view(), name='import-bulletins'),

    url(r'^attribution/$', views.AttributionView.as_view(), name='attribution'),
    url(r'^stages/export/(?P<scope>all)?/?$', views.stages_export, name='stages_export'),

    url(r'^institutions/$', views.CorporationListView.as_view(), name='corporations'),
    url(r'^institutions/(?P<pk>\d+)/$', views.CorporationView.as_view(), name='corporation'),
    url(r'^classes/$', views.KlassListView.as_view(), name='classes'),
    url(r'^classes/(?P<pk>\d+)/$', views.KlassView.as_view(), name='class'),

    url(r'^imputations/export/$', views.imputations_export, name='imputations_export'),
    url(r'^print/update_form/$', views.print_update_form, name='print_update_form'),
    url(r'^general_export/$', views.general_export, name='general-export'),
    url(r'^ortra_export/$', views.ortra_export, name='ortra-export'),

    # AJAX/JSON urls
    url(r'^section/(?P<pk>\d+)/periods/', views.section_periods, name='section_periods'),
    url(r'^section/(?P<pk>\d+)/classes/', views.section_classes, name='section_classes'),
    url(r'^period/(?P<pk>\d+)/students/', views.period_students, name='period_students'),
    url(r'^period/(?P<pk>\d+)/corporations/', views.period_availabilities, name='period_availabilities'),
    # Training params in POST:
    url(r'^training/new/', views.new_training, name="new_training"),
    url(r'^training/del/', views.del_training, name="del_training"),
    url(r'^training/by_period/(?P<pk>\d+)/', views.TrainingsByPeriodView.as_view()),

    url(r'^student/(?P<pk>\d+)/summary/', views.StudentSummaryView.as_view()),
    url(r'^availability/(?P<pk>\d+)/summary/', views.AvailabilitySummaryView.as_view()),
    url(r'^corporation/(?P<pk>\d+)/contacts/', views.CorpContactJSONView.as_view()),
]
