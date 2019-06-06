from events import views
from django.urls import path

urlpatterns = [
    path('events/<int:event_id>', views.EventView.as_view(),
         name='event_details'),
    path('events/', views.EventsView.as_view(),
         name='event_list_and_create_new'),
    path('events/<int:event_id>/images', views.EventImageUploadView.as_view(),
         name='upload_images_for_an_event'),
    path('events/<int:event_id>/like-toggle', views.like_event,
         name='like_an_event'),
    path('events/<int:event_id>/participation-toggle', views.participate_event,
         name='participate_an_event'),
    path('events/<int:event_id>/comments', views.comment_event,
         name='comment_on_an_event'),
    path('events/<int:event_id>/comments/<int:comment_id>', views.edit_comment_event,
         name='edit_comment_on_an_event')
]
