from django.shortcuts import render, redirect

# Create your views here.
def taste_map(request):
    return render(request, 'store/taste_map.html')