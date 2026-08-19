from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg

from .models import Blog, Rate , Comments

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

    comments = Comments.objects.filter(
        blog=blog,
        level = 0,
    ).prefetch_related('replies')



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
            'comments':comments
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
def blog_comment(request):
    if request.method != 'POST':
        return JsonResponse({
            'success':False,
            'error':'Invalid request'
        })
    #check login
    if not request.user.is_authenticated:
        return JsonResponse({
            'success':False,
            'login_required':True,
            'error':'Vui lòng đăng nhập để comment'
        })
    # lấy user hiện tại
    user = request.user
    userName = user.username
    userId = user.id
    if user.avatar:
        userImages = user.avatar.url
    else:
        userImages = ''

    #lấy dữ liệu từ ajax
    blog_id = request.POST.get('blog_id')
    comment = request.POST.get('comment')
    parent_id = request.POST.get('parent_id')

    #ktra comment
    if not comment or not comment.strip():
        return JsonResponse({
            'success':False,
            'error':'Vui lòng comment'
        })
    #ktra blog
    blog = get_object_or_404(Blog, id=blog_id)

    #xác định comment cha
    parent = None
    level = 0

    if parent_id:
        parent = get_object_or_404(Comments, id = parent_id)
        level = 1

    #lưu comment

    new_comment = Comments.objects.create(
        comment = comment.strip(),
        author_name = userName,
        author_image = userImages,
        blog = blog,
        author_id = userId,
        parent = parent,
        level= level
    )

    #data trả về ajax
    comment_data = {
        'id': new_comment.id,
        'comment': new_comment.comment,
        'author_name': new_comment.author_name,
        'author_image': new_comment.author_image,
        'blog_id': new_comment.blog_id,
        'author_id': new_comment.author_id,
        'parent_id': new_comment.parent_id,
        'level' : new_comment.level,
        'created':new_comment.created.strftime(
            '%d/%m/%Y %H:%M'
        )
    }
    return JsonResponse({
        'success':True,
        'data':comment_data
    })
