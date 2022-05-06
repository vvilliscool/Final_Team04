from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from utils.decorators import login_required
from django.views.decorators.http import require_POST

from member.models import Like
from .models import Review, Comment
from .forms import CommentForm, ReviewForm
# Create your views here.



def review_list(request):
    reviews = Review.objects.all()
    comment_form = CommentForm()
    comments = Comment.objects.all()
    context = {
        'reviews': reviews,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'review/review_list.html', context)


@login_required
def comment_create(request, review_pk):
    # GET 파라미터로 전달된 작업 완료 후 이동할 URL값
    next_path = request.GET.get('next')

    # 요청 메서드가 POST방식 일 때만 처리
    if request.method == 'POST':
        # Post인스턴스를 가져오거나 404 Response를 돌려줌
        review = get_object_or_404(Review, pk=review_pk)
        # request.POST데이터를 이용한 Bounded Form생성
        comment_form = CommentForm(request.POST)

        # 올바른 데이터가 Form인스턴스에 바인딩 되어있는지 유효성 검사
        if comment_form.is_valid():
            # 유효성 검사에 통과하면 ModelForm의 save()호출로 인스턴스 생성
            # DB에 저장하지 않고 인스턴스만 생성하기 위해 commit=False옵션 지정
            comment = comment_form.save(commit=False)
            # CommentForm에 지정되지 않았으나 필수요소인 author와 review속성을 지정
            comment.review = review
            comment.author = request.user
            # DB에 저장
            comment.save()

            # 성공 메시지를 다음 request의 결과로 전달하도록 지정
            messages.success(request, '댓글이 등록되었습니다')
        else:
            # 유효성 검사에 실패한 경우
            # 에러 목록을 순회하며 에러메시지를 작성, messages의 error레벨로 추가
            error_msg = '댓글 등록에 실패했습니다\n{}'.format(
                '\n'.join(
                    [f'- {error}'
                     for key, value in comment_form.errors.items()
                     for error in value]))
            messages.error(request, error_msg)

        # next 파라미터에 값이 담겨온 경우에 그 경로로 이동
        if next_path:
            return redirect(next_path)
        # 'review'네임스페이스를 가진 url의 'post_list'이름에 해당하는 뷰로 이동
        return redirect('review:review_list')



def review_detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm()
    comments = Comment.objects.all()
    context = {
        'review': review,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'review/review_detail.html', context)


@login_required
def review_create(request):
    if request.method == 'POST':
        # PostForm은 파일을 처리하므로 request.FILES도 함께 바인딩
        review_form = ReviewForm(request.POST, request.FILES)
        print(request.user)
        if review_form.is_valid():
            # author필드를 채우기 위해 인스턴스만 생성
            review = review_form.save(commit=False)
            # author필드를 채운 후 DB에 저장
            review.author = request.user
            review.save()

            # 성공 알림을 messages에 추가 후 review_list뷰로 이동
            messages.success(request, '리뷰가 등록되었습니다')
            return redirect('review:review_list')
    else:
        review_form = ReviewForm()

    context = {
        'review_form': review_form,
    }
    return render(request, 'review/review_create.html', context)


# 좋아요 기능
@login_required
def review_like_toggle(request, review_pk):
    # GET파라미터로 전달된 이동할 URL
    next_path = request.GET.get('next')
    # review_pk에 해당하는 Review객체
    review = get_object_or_404(Review, pk=review_pk)
    # 요청한 사용자
    user = request.user

    # 사용자의 like_reviews목록에서 like_toggle할    Review가 있는지 확인
    filtered_like_reviews = user.like_reviews.filter(pk=review.pk)
    # 존재할경우, like_reviews목록에서 해당 Review를 삭제
    if filtered_like_reviews.exists():
        user.like_reviews.remove(review)
    # 없을 경우, like_posts목록에 해당 Review를 추가
    else:
        user.like_reviews.add(review)

    # 이동할 path가 존재할 경우 해당 위치로, 없을 경우 Review상세페이지로 이동
    if next_path:
        return redirect(next_path)
    return redirect('review:review_detail', review_pk=review_pk)



# 리뷰 편집
@login_required
def review_edit(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if review.author == request.user:
        if request.method == 'POST':
            review_form =  ReviewForm(request.POST, request.FILES, instance=review)
            if review_form.is_valid():
                review_form.save()
                return redirect('review:review_list')
        else:
            review_form = ReviewForm()
        
    context = {
        'review_form': review_form,
    }
    return render(request, 'review/review_edit.html', context)    


# 리뷰 삭제
@login_required
# @require_POST
def review_delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    print(request.user)
    print(review.author)
    if review.author == request.user:
        review.delete()
    return redirect('review:review_list')
