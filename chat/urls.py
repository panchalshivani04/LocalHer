from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('start/<slug:seller_slug>/', views.start_chat_view, name='start_chat'),
    path('t/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('t/<int:conversation_id>/delete/', views.delete_conversation_view, name='delete_conversation'),
    path('media/<int:message_id>/', views.protected_chat_media_view, name='protected_chat_media'),
    path('api/messages/<int:conversation_id>/', views.api_get_messages, name='chat_api_get_messages'),
    path('api/send/<int:conversation_id>/', views.api_send_message, name='chat_api_send_message'),
    path('api/unread-count/', views.api_unread_count, name='chat_api_unread_count'),
    path('api/unsend/<int:message_id>/', views.api_unsend_message, name='chat_api_unsend_message'),
    path('api/block/<int:target_user_id>/', views.api_toggle_block_user, name='chat_api_toggle_block'),
    path('api/report/', views.api_submit_report, name='chat_api_submit_report'),
]
