from django.urls import path
from django.urls.conf import include
from . import views
# from rest_framework.routers import SimpleRouter,DefaultRouter
from rest_framework_nested import routers
router = routers.DefaultRouter()

router.register('pathologypictureitems',views.PathologyPictureItemViewSet)
router.register('diagnosisitems',views.DiagnosisItemViewSet)
router.register('diagnoses',views.DiagnosisViewSet,basename="diagnoses")
router.register('report',views.ReportViewSet)

diagnosisitems_router = routers.NestedDefaultRouter(router,r'diagnosisitems',lookup = 'diagnosisitem')
diagnosisitems_router.register('labelitems',views.LabelItemViewSet,basename='diagnosisitem-labelitem')
urlpatterns =[
    path('',include(router.urls)),
    path('',include(diagnosisitems_router.urls)),
    path('generatedoc', views.generateDocument)

]