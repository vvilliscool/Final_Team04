from django.shortcuts import render, redirect

def index(request):
    return render(request, 'index.html')

def ranking(request):
    return render(request, 'ranking.html')

def map(request):
    return render(request, 'map.html')

def mypage(request):
    return render(request, 'mypage.html')
