from accounts import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # authentication
    path('login/', views.LoginView.as_view(),
         name='login'),
    path('logout/', views.LogoutView.as_view(),
         name='logout'),
    # admin CRUD visitors
    path('admin/visitors/<int:visitor_id>', views.VisitorView.as_view(),
         name='vistor detail'),
    path('admin/visitors/', views.VisitorsView.as_view(),
         name='view list and create visitor'),
]

urlpatterns = format_suffix_patterns(urlpatterns)