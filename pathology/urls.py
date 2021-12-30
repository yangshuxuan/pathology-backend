from django.urls import path
from django.urls.conf import include
from . import views
# from rest_framework.routers import SimpleRouter,DefaultRouter
from rest_framework_nested import routers
router = routers.DefaultRouter()

router.register('pathologypictureitems',views.PathologyPictureItemViewSet)
pathologypictureitems_router = routers.NestedDefaultRouter(router,r'pathologypictureitems',lookup = 'pathologypictureitem')
pathologypictureitems_router.register('labelitems',views.LabelItemViewSet,basename='pathologypictureitem-labelitem')
urlpatterns =[
    path('',include(router.urls)),
    path('',include(pathologypictureitems_router.urls)),
    path('generatedoc', views.generateDocument)

]