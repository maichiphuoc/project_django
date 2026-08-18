from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg

from .models import Blog, Rate

def blog_list(request):

    blogs = Blog.objects.all().order_by('-created_at')

    paginator = Paginator(blogs, 3)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'Blog/blog_list.html',
        {
            'page_obj': page_obj
        }
    )
def blog_detail(request, blog_id):

    # Lấy bài viết đang click
    blog = get_object_or_404(
        Blog,
        id=blog_id
    )
    #bai viet truoc
    previous_blog = Blog.objects.filter(
        created_at__gt=blog.created_at
    ).order_by(
        'created_at'
    ).first()
    #bai viet tiep theo
    next_blog = Blog.objects.filter(
        created_at__lt=blog.created_at
    ).order_by(
        '-created_at'
    ).first()

    #Tính tbinh
    average_result = Rate.objects.filter(
        blog=blog
    ).aggregate(
        average=Avg('rate')
    )

    average_rate = average_result['average'] or 0

    # Điểm trung bình hiển thị
    average_rate = round(average_rate, 1)

    # Round điểm trung bình được tô
    average_star = round(average_rate)


    # lấy điểm user đánh giá

    user_rate = None

    if request.user.is_authenticated:

        user_rate = Rate.objects.filter(
            blog=blog,
            author=request.user
        ).first()

        if user_rate:
            user_rate = user_rate.rate


    return render(
        request,
        'Blog/blog_detail.html',
        {
            'blog': blog,
            'previous_blog': previous_blog,
            'next_blog': next_blog,

            'average_rate': average_rate,

            'user_rate': user_rate,

            'average_star': average_star,

            'star_range': range(1, 6),
        }
    )

#Ajax rate
def blog_rate(request):
    #chỉ cho phép post
    if request.method != 'POST':

        return JsonResponse({
            'success': False,
            'error': 'Invalid request'
        }, status=400)
    #check login
    if not request.user.is_authenticated:

        return JsonResponse({
            'success': False,
            'error': 'Vui lòng đăng nhập'
        }, status=401)

    #lấy dữ liệu từ ajax
    blog_id = request.POST.get('blog_id')

    rate = request.POST.get('rate')

    #ktra data
    if not blog_id or not rate:

        return JsonResponse({
            'success': False,
            'error': 'Thiếu dữ liệu'
        }, status=400)


    #chuyen dổi kiểu dữ liệu
    try:

        rate = int(rate)
        blog_id = int(blog_id)

    except ValueError:

        return JsonResponse({
            'success': False,
            'error': 'Dữ liệu không hợp lệ'
        }, status=400)

    #ktra đánh giá
    if rate < 1 or rate > 5:

        return JsonResponse({
            'success': False,
            'error': 'Điểm đánh giá phải từ 1 đến 5'
        }, status=400)


    # lấy blog
    blog = get_object_or_404(
        Blog,
        id=blog_id
    )

    #lưu và cập nhật đánh giá
    Rate.objects.update_or_create(
        blog=blog,
        author=request.user,
        defaults={
            'rate': rate
        }
    )


    #tinh lại diem tbinh
    average_result = Rate.objects.filter(
        blog=blog
    ).aggregate(
        average=Avg('rate')
    )

    average_rate = average_result['average'] or 0


    # Round điểm trung bình
    average_rate = round(average_rate)

    # trả json về js
    return JsonResponse({

        'success': True,

        # Điểm user vừa chọn
        'rate': rate,

        # Điểm trung bình
        'average_rate': average_rate

    })