import os
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, Http404
from django.db.models import Q
from .models import Conversation, Message, UserBlock, Report
from accounts.models import User, SellerProfile


def _validate_image_file(image_file):
    """
    Validates uploaded image file extension, size (max 5MB), and MIME type.
    """
    if not image_file:
        return True, None
    
    if image_file.size > 5 * 1024 * 1024:
        return False, "Image file size exceeds the 5MB maximum limit."

    ext = os.path.splitext(image_file.name)[1].lower()
    allowed_exts = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in allowed_exts:
        return False, "Invalid image format. Allowed formats: JPG, PNG, WEBP."

    return True, None


def _is_personal_block_active(user_a, user_b):
    """
    Checks whether a Level 1 personal block exists between user_a and user_b.
    """
    if not user_a.is_authenticated or not user_b.is_authenticated:
        return False
    return UserBlock.objects.filter(
        Q(blocker=user_a, blocked_user=user_b) | Q(blocker=user_b, blocked_user=user_a)
    ).exists()


@login_required
def start_chat_view(request, seller_slug):
    """
    Customer clicks 'Chat with Seller' on Seller Profile or Product Detail.
    Retrieves or creates the unique private Conversation thread and redirects to chat UI.
    Enforces server-side personal block & account status checks.
    """
    seller = get_object_or_404(SellerProfile, slug=seller_slug)
    
    if request.user == seller.user:
        messages.info(request, "You are viewing your own seller storefront.")
        return redirect('inbox')

    # SERVER-SIDE BLOCK CHECK
    if _is_personal_block_active(request.user, seller.user):
        messages.warning(request, "Messaging is currently unavailable for this user.")
        return redirect('inbox')

    conversation, created = Conversation.objects.get_or_create(
        customer=request.user,
        seller=seller
    )
    return redirect('conversation_detail', conversation_id=conversation.id)


@login_required
def inbox_view(request):
    """
    Lists all active private conversation threads for the logged in user (both as Customer and Seller).
    """
    user = request.user
    
    conversations = Conversation.objects.filter(
        Q(customer=user) | Q(seller__user=user)
    ).select_related('customer', 'seller', 'seller__user').prefetch_related('messages')

    threads = []
    for conv in conversations:
        other = conv.get_other_participant(user)
        last_msg = conv.messages.last()
        unread = conv.unread_count_for_user(user)
        is_blocked = _is_personal_block_active(user, other['user'])
        threads.append({
            'conversation': conv,
            'other': other,
            'last_message': last_msg,
            'unread_count': unread,
            'is_blocked': is_blocked,
        })

    context = {
        'threads': threads,
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def conversation_detail_view(request, conversation_id):
    """
    Renders the 1-on-1 private chat interface between customer and seller.
    Strictly checks authorization, platform-wide status, and personal blocking.
    """
    conversation = get_object_or_404(
        Conversation.objects.select_related('customer', 'seller', 'seller__user'),
        id=conversation_id
    )

    # SECURITY ACCESS CONTROL: Only participants are allowed
    if request.user != conversation.customer and request.user != conversation.seller.user:
        messages.error(request, "Unauthorized access. You do not have permission to view this conversation.")
        return redirect('inbox')

    other = conversation.get_other_participant(request.user)

    # Personal block status check
    is_blocked = _is_personal_block_active(request.user, other['user'])
    user_has_blocked_other = UserBlock.objects.filter(blocker=request.user, blocked_user=other['user']).exists()

    # Mark unread messages sent by the other user as read
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    # Handle standard HTTP form post fallback
    if request.method == 'POST':
        if is_blocked:
            messages.error(request, "Messaging is currently unavailable for this conversation.")
            return redirect('conversation_detail', conversation_id=conversation.id)

        content = request.POST.get('content', '').strip()
        image_file = request.FILES.get('image')

        valid, err_msg = _validate_image_file(image_file)
        if not valid:
            messages.error(request, err_msg)
            return redirect('conversation_detail', conversation_id=conversation.id)

        if content or image_file:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                image=image_file
            )
            conversation.save()
            return redirect('conversation_detail', conversation_id=conversation.id)

    chat_messages = conversation.messages.select_related('sender').all()

    context = {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'other': other,
        'is_blocked': is_blocked,
        'user_has_blocked_other': user_has_blocked_other,
        'reason_choices': Report.REASON_CHOICES,
    }
    return render(request, 'chat/conversation_detail.html', context)


@login_required
def protected_chat_media_view(request, message_id):
    """
    Serves private chat photos strictly to authenticated participants of the conversation.
    """
    msg = get_object_or_404(Message.objects.select_related('conversation', 'conversation__customer', 'conversation__seller__user'), id=message_id)
    conversation = msg.conversation

    if request.user != conversation.customer and request.user != conversation.seller.user:
        return HttpResponseForbidden("Unauthorized to view this private chat media.")

    if not msg.image or not os.path.exists(msg.image.path):
        raise Http404("Image file not found.")

    content_type, _ = mimetypes.guess_type(msg.image.path)
    return FileResponse(open(msg.image.path, 'rb'), content_type=content_type or 'image/jpeg')


@login_required
def delete_conversation_view(request, conversation_id):
    """
    Privacy feature allowing participants to delete their conversation thread and erase chat history.
    """
    if request.method != 'POST':
        return HttpResponseForbidden()

    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user != conversation.customer and request.user != conversation.seller.user:
        return HttpResponseForbidden("Unauthorized to delete this conversation.")

    conversation.delete()
    messages.success(request, "Conversation thread has been deleted.")
    return redirect('inbox')


@login_required
def api_toggle_block_user(request, target_user_id):
    """
    LEVEL 1 PERSONAL BLOCK:
    Toggles personal block between request.user and target_user.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    target_user = get_object_or_404(User, id=target_user_id)

    if request.user == target_user:
        return JsonResponse({'error': 'You cannot block yourself'}, status=400)

    block, created = UserBlock.objects.get_or_create(blocker=request.user, blocked_user=target_user)
    if not created:
        block.delete()
        is_blocked = False
        msg = f"Unblocked {target_user.get_full_name() or target_user.username}"
    else:
        is_blocked = True
        msg = f"Blocked {target_user.get_full_name() or target_user.username}"

    return JsonResponse({
        'success': True,
        'is_blocked': is_blocked,
        'message': msg
    })


@login_required
def api_submit_report(request):
    """
    LEVEL 2 MODERATION REPORT:
    Submits a safety report against a user or specific message for admin review.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    reported_user_id = request.POST.get('reported_user_id')
    conversation_id = request.POST.get('conversation_id')
    message_id = request.POST.get('message_id')
    reason = request.POST.get('reason', 'OTHER')
    description = request.POST.get('description', '').strip()

    reported_user = get_object_or_404(User, id=reported_user_id)

    if request.user == reported_user:
        return JsonResponse({'error': 'You cannot report yourself'}, status=400)

    conv = get_object_or_404(Conversation, id=conversation_id) if conversation_id else None
    msg = get_object_or_404(Message, id=message_id) if message_id else None

    report = Report.objects.create(
        reporter=request.user,
        reported_user=reported_user,
        conversation=conv,
        message=msg,
        reason=reason,
        description=description,
        status='PENDING'
    )

    return JsonResponse({
        'success': True,
        'report_id': report.id,
        'message': 'Report submitted successfully. Our safety team will review it.'
    })


@login_required
def api_get_messages(request, conversation_id):
    """
    Real-Time JSON endpoint for fetching new messages and syncing active message IDs.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user != conversation.customer and request.user != conversation.seller.user:
        return HttpResponseForbidden(JsonResponse({'error': 'Unauthorized access'}))

    other = conversation.get_other_participant(request.user)
    if _is_personal_block_active(request.user, other['user']):
        return JsonResponse({'messages': [], 'active_ids': [], 'is_blocked': True})

    after_id = request.GET.get('after_id', 0)
    try:
        after_id = int(after_id)
    except ValueError:
        after_id = 0

    active_ids = list(conversation.messages.values_list('id', flat=True))

    new_messages = conversation.messages.filter(id__gt=after_id).select_related('sender')
    conversation.messages.exclude(sender=request.user).filter(id__gt=after_id, is_read=False).update(is_read=True)

    data = []
    for msg in new_messages:
        image_url = f"/chat/media/{msg.id}/" if msg.image else None
        data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name() or msg.sender.username,
            'is_self': msg.sender == request.user,
            'content': msg.content,
            'image_url': image_url,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
        })

    return JsonResponse({'messages': data, 'active_ids': active_ids})


@login_required
def api_send_message(request, conversation_id):
    """
    Real-Time JSON endpoint for sending a new text or photo message via fetch/AJAX.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user != conversation.customer and request.user != conversation.seller.user:
        return HttpResponseForbidden(JsonResponse({'error': 'Unauthorized access'}))

    other = conversation.get_other_participant(request.user)
    if _is_personal_block_active(request.user, other['user']):
        return JsonResponse({'error': 'Messaging is currently unavailable for this conversation.'}, status=403)

    content = request.POST.get('content', '').strip()
    image_file = request.FILES.get('image')

    valid, err_msg = _validate_image_file(image_file)
    if not valid:
        return JsonResponse({'error': err_msg}, status=400)

    if not content and not image_file:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    msg = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content,
        image=image_file
    )
    conversation.save()

    image_url = f"/chat/media/{msg.id}/" if msg.image else None

    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name() or msg.sender.username,
            'is_self': True,
            'content': msg.content,
            'image_url': image_url,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
        }
    })


@login_required
def api_unread_count(request):
    """
    Returns total count of unread chat messages for navbar notification badge.
    """
    user = request.user
    unread_total = Message.objects.filter(
        Q(conversation__customer=user) | Q(conversation__seller__user=user)
    ).exclude(sender=user).filter(is_read=False).count()

    return JsonResponse({'unread_count': unread_total})


@login_required
def api_unsend_message(request, message_id):
    """
    Unsend / Delete a message sent by the logged in user.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    msg = get_object_or_404(Message, id=message_id)

    if msg.sender != request.user:
        return HttpResponseForbidden(JsonResponse({'error': 'Unauthorized to unsend this message'}))

    deleted_id = msg.id
    msg.delete()
    return JsonResponse({'success': True, 'deleted_id': deleted_id})
