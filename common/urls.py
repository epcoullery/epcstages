from django.conf.urls import patterns, include, url
from django.contrib import admin

from stages import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'epcstages.views.home', name='home'),
    # url(r'^epcstages/', include('epcstages.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^attribution/$', views.AttributionView.as_view(), name='attribution'),
    url(r'^stages/export/$', 'stages.views.stages_export', name='stages_export'),

    # AJAX/JSON urls
    url(r'^section/(?P<pk>\d+)/periods/', 'stages.views.section_periods'),
    url(r'^period/(?P<pk>\d+)/students/', 'stages.views.period_students'),
    url(r'^period/(?P<pk>\d+)/corporations/', 'stages.views.period_availabilities'),
    # Training params in POST:
    url(r'^training/new/', 'stages.views.new_training'),
    url(r'^training/by_period/(?P<pk>\d+)/', views.TrainingsByPeriodView.as_view()),

    url(r'^student/(?P<pk>\d+)/summary/', views.StudentSummaryView.as_view()),
    url(r'^availability/(?P<pk>\d+)/summary/', views.AvailabilitySummaryView.as_view()),
)
