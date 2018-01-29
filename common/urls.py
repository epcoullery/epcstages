from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from candidats import views as candidats_views
from stages import views

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True), name='home'),

    path('admin/', admin.site.urls),
    path('import_students/', views.StudentImportView.as_view(), name='import-students'),
    path('import_hp/', views.HPImportView.as_view(), name='import-hp'),
    path('import_hp_contacts/', views.HPContactsImportView.as_view(), name='import-hp-contacts'),
    path('import_bulletins/', views.ImportBulletinView.as_view(), name='import-bulletins'),

    path('attribution/', views.AttributionView.as_view(), name='attribution'),
    re_path(r'^stages/export/(?P<scope>all)?/?$', views.stages_export, name='stages_export'),

    path('institutions/', views.CorporationListView.as_view(), name='corporations'),
    path('institutions/<int:pk>/', views.CorporationView.as_view(), name='corporation'),
    path('classes/', views.KlassListView.as_view(), name='classes'),
    path('classes/<int:pk>/', views.KlassView.as_view(), name='class'),

    path('candidate/<int:pk>/send_convocation/', candidats_views.SendConvocationView.as_view(),
        name='candidate-convocation'),

    path('imputations/export/', views.imputations_export, name='imputations_export'),
    path('print/update_form/', views.print_update_form, name='print_update_form'),
    path('general_export/', views.general_export, name='general-export'),
    path('ortra_export/', views.ortra_export, name='ortra-export'),

    # AJAX/JSON urls
    path('section/<int:pk>/periods/', views.section_periods, name='section_periods'),
    path('section/<int:pk>/classes/', views.section_classes, name='section_classes'),
    path('period/<int:pk>/students/', views.period_students, name='period_students'),
    path('period/<int:pk>/corporations/', views.period_availabilities, name='period_availabilities'),
    # Training params in POST:
    path('training/new/', views.new_training, name="new_training"),
    path('training/del/', views.del_training, name="del_training"),
    path('training/by_period/<int:pk>/', views.TrainingsByPeriodView.as_view()),

    path('student/<int:pk>/summary/', views.StudentSummaryView.as_view()),
    path('availability/<int:pk>/summary/', views.AvailabilitySummaryView.as_view()),
    path('corporation/<int:pk>/contacts/', views.CorpContactJSONView.as_view()),
]
