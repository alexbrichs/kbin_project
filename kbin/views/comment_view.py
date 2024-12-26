from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from ..models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

@login_required(redirect_field_name='login')
@csrf_exempt
def add_comment(request, thread_id):
    thread = Publicacio.objects.get(pk=thread_id)
    if request.method == 'POST':
        body = request.POST.get('entry_comment[body]')
        if body:
            user_email = request.user.email
            user = User.objects.get(email=user_email)
            comment = Comment(body=body, author=user, thread=thread, creation_data=timezone.now())
            comment.save()
            thread.num_coments += 1
            thread.save()
    order = request.session.get('order')
    request.session['order'] = order
    return redirect('veure_thread', thread_id=thread_id, order=order)

@login_required(redirect_field_name='login')
@csrf_exempt
def add_reply(request, thread_id, comment_id):
    comment_root = Comment.objects.get(pk=comment_id)
    thread = Publicacio.objects.get(pk=thread_id)
    if request.method == 'POST':
        body = request.POST.get('entry_comment[body]')
        if body:
            user_email = request.user.email
            user = User.objects.get(email=user_email)
            comment_reply = Comment(body=body, author=user, thread=thread, creation_data=timezone.now(),
                                    level=comment_root.level + 1)
            comment_reply.save()
            reply = Reply(comment_root=comment_root, comment_reply=comment_reply)
            reply.save()
            thread.num_coments += 1
            thread.save()
    order = request.session.get('order')
    request.session['order'] = order
    return redirect('veure_thread', thread_id=thread.id, order=order)

@login_required(redirect_field_name='login')
@csrf_exempt
def like_comment(request, thread_id, comment_id):
    if request.method == 'POST':
        user_email = request.user.email
        user = User.objects.get(email=user_email)
        comment = Comment.objects.get(pk=comment_id)
        if not Vote_comment.objects.filter(comment=comment, user=user, type='like').exists():
            comment.num_likes += 1
            if Vote_comment.objects.filter(comment=comment, user=user, type='dislike').exists():
                comment.num_dislikes -= 1
                vote = Vote_comment.objects.get(comment=comment, user=user)
                vote.delete()
            new_vote = Vote_comment(comment=comment, user=user, type='like')
            new_vote.save()
        else:
            comment.num_likes -= 1
            vote = Vote_comment.objects.get(comment=comment, user=user)
            vote.delete()
        comment.save()
        order = request.session.get('order')
        request.session['order'] = order
        return redirect('veure_thread', thread_id=thread_id, order=order)
    else:
        return redirect('main')

@login_required(redirect_field_name='login')
@csrf_exempt
def dislike_comment(request, thread_id, comment_id):
    if request.method == 'POST':
        user_email = request.user.email
        user = User.objects.get(email=user_email)
        comment = Comment.objects.get(pk=comment_id)
        if not Vote_comment.objects.filter(comment=comment, user=user, type='dislike').exists():
            comment.num_dislikes += 1
            if Vote_comment.objects.filter(comment=comment, user=user, type='like').exists():
                comment.num_likes -= 1
                vote = Vote_comment.objects.get(comment=comment, user=user)
                vote.delete()
            new_vote = Vote_comment(comment=comment, user=user, type='dislike')
            new_vote.save()
        else:
            comment.num_dislikes -= 1
            vote = Vote_comment.objects.get(comment=comment, user=user)
            vote.delete()
        comment.save()
        order = request.session.get('order')
        request.session['order'] = order
        return redirect('veure_thread', thread_id=thread_id, order=order)
    else:
        return redirect('main')

@login_required(redirect_field_name='login')
@csrf_exempt
def edit_comment(request, thread_id, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if request.method == 'POST':
        body = request.POST.get('entry_comment[body]')
        if body:
            comment.body = body
            comment.last_edited = timezone.now()
            comment.save()
    order = request.session.get('order')
    request.session['order'] = order
    return redirect('veure_thread', thread_id=thread_id, order=order)

@login_required(redirect_field_name='login')
@csrf_exempt
def delete_comment(request, thread_id, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    replies = Reply.objects.filter(comment_root=comment)
    thread = Publicacio.objects.get(pk=thread_id)
    for reply in replies:
        reply_comment = reply.comment_reply
        reply_comment.delete()
        thread.num_coments -= 1
        thread.save()
    thread.num_coments -= 1
    thread.save()
    comment.delete()
    order = request.session.get('order')
    request.session['order'] = order
    return redirect('veure_thread', thread_id=thread_id, order=order)
