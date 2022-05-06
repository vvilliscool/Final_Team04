from re import U
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.db.models import Count

from .forms import LoginForm, SignupForm, ModifyForm
from .models import User, Like
from review.models import Review, Comment
from collections import Counter

def login(request):
    if request.method == 'POST':
        
        # Data bounded form인스턴스 생성
        
        
        # Ver.1
        # login_form = LoginForm(request.POST)    
        # # 유효성 검증에 성공할 경우
        # if login_form.is_valid():
        #     # form으로부터 id, password값을 가져옴
        #     username = login_form.cleaned_data['username']
        #     password = login_form.cleaned_data['password']

        #     # 가져온 id과 password에 해당하는 User가 있는지 판단한다
        #     # 존재할경우 user변수에는 User인스턴스가 할당되며,
        #     # 존재하지 않으면 None이 할당된다
        #     user = authenticate(
        #         username=username,
        #         password=password
        #     )
        #     # 인증에 성공했을 경우
        #     if user:
        #         # Django의 auth앱에서 제공하는 login함수를 실행해 앞으로의 요청/응답에 세션을 유지한다
        #         django_login(request, user)
        #         # Post목록 화면으로 이동
        #         return redirect('review:review_list')


        # Ver.2
        # 로그인 성공 후 이동할 URL. 주어지지 않으면 None
        next = request.GET.get('next')
        # AuthenticationForm의 첫 번째 인수는 해당 request가 되어야 한다
        login_form = LoginForm(request=request, data=request.POST)

        # 유효성 검증에 성공할 경우
        # AuthenticationForm을 사용하면 authenticate과정까지 완료되어야 유효성 검증을 통과한다
        if login_form.is_valid():
            # AuthenticatonForm에서 인증(authenticate)에 성공한 유저를 가져오려면 이 메서드를 사용한다
            user = login_form.get_user()
            # Django의 auth앱에서 제공하는 login함수를 실행해 앞으로의 요청/응답에 세션을 유지한다
            django_login(request, user)
            # next가 존재하면 해당 위치로, 없으면 Post목록 화면으로 이동
            return redirect(next if next else 'review:review_list')


            # 인증에 실패하면 login_form에 non_field_error를 추가한다
        login_form.add_error(None, '아이디 또는 비밀번호가 올바르지 않습니다')
    else:
        login_form = LoginForm()
    context = {
        'login_form': login_form,
    }
    return render(request, 'member/login.html', context)


def logout(request):
    django_logout(request)
    return redirect('review:review_list')


def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, request.FILES)
        # 유효성 검증에 통과한 경우 (id, 이메일, 닉네임의 중복과 password1, 2의 일치 여부)
        if signup_form.is_valid():
            
            # Ver.1
            # SignupForm의 인스턴스 메서드인 signup() 실행, 유저 생성
            # signup_form.signup()
            
            # Ver.2
            # 이미지를 DB에 저장하기 위해서..
            user = signup_form.save(commit=False)
            # user.img_profile = signup_form.cleaned_data['img_profile']
            user.save()
            django_login(request, user)
            
            
            return redirect('review:review_list')
    else:
        signup_form = SignupForm()

    context = {
        'signup_form': signup_form,
    }
    return render(request, 'member/signup.html', context)



def ranking(request):
    users = User.objects.all()
    reviews = Review.objects.all().order_by('-pk')
    comments = Comment.objects.all()
    
    # 리뷰 작성 수를 기준으로 내림차순으로 정렬(작성자, 작성 리뷰 수)
    review_counts = Review.objects.values('author').order_by('author').annotate(count=Count('author'))
    print(review_counts)
    # 좋아요 수 조인 도전


    # 랭커 관련 정보 가져오기
    like_join = Like.objects.select_related('review_id')
    like_rank = []
    for obj in like_join:
        like_rank.append(obj.review_id.author.username)
    rank = dict(Counter(like_rank).most_common())
    # 유저 이름
    rank_names = list(rank.keys())
    # 유저가 받은 좋아요 수
    rank_like_nums = list(rank.values())
    # 유저 ID
    rank_objs = User.objects.filter(username__in=rank_names)
    rank_user_ids = []
    for user in rank_objs:
        rank_user_ids.append(user.id)
    # 정렬
    rank_user_ids.sort()
    # 랭커의 이름, 좋아요 수, user_id를 zip화 시킨다.
    rank_list = zip(rank_names, rank_like_nums, rank_user_ids)
   
    context = {
        'users': users,
        'reviews': reviews,
        'comments': comments,
        'review_counts': review_counts,
        'rank_objs':rank_objs,
        'rank_like_nums':rank_like_nums,
        'rank_names':rank_names,
        'rank_list' : rank_list,
    }
    return render(request, 'member/ranking.html', context)


# 마이 페이지
def mypage(request):
    # 현재 접속한 유저 정보(인덱싱으로 쿼리셋 풀어서 객체 하나만 보내기)
    user = User.objects.filter(username=request.user)[0]
    # 현재 접속한 유저가 작성한 리뷰들
    reviews = Review.objects.filter(author=request.user).order_by('-pk')

    # 현재 접속한 유저가 작성한 리뷰 수
    review_counts = len(reviews)
    
    # 현재 접속한 유저가 리뷰를 작성해서 받은 좋아요 수
    likes = Like.objects.select_related('review_id')
    like_counts = 0
    for like in likes:
        if like.review_id.author == request.user:
            like_counts += 1
    
    context = {
        'user':user,
        'reviews':reviews,
        'review_counts':review_counts,
        'like_counts':like_counts,
    }
    return render(request, 'member/mypage.html', context)


# 프로필(유저) 정보 수정
def modify(request):
    user = User.objects.filter(username=request.user)[0]
    print(request.user)
    if request.method == 'POST':
        modify_form = ModifyForm(request.POST, request.FILES, instance=request.user)
        
        if modify_form.is_valid():
            modify_form.save()
            return redirect('member:mypage')
    else:
        modify_form= ModifyForm()

    context = {
        'modify_form': modify_form,
        'user':user,
    }
    return render(request, 'member/modify.html', context)