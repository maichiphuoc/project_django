import os
import json
from django.urls import reverse
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import registerForm,loginForm, accountForm
from .models import Country,Product,Category,Brand
from django.conf import settings
from django.contrib.auth.hashers import make_password
from PIL import Image

#ajax
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

# Create your views here.
# def index(request):
#     return render(request,'Users/index.html')

def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            user.set_password(
                form.cleaned_data['password']
            )
            user.is_superuser = False
            user.is_staff = False

            user.save()
            return redirect('login')
    else:
        form = registerForm()
    return render(request,'Users/register.html',{'form':form})
def login_view(request):
    if request.method == 'POST':
        form = loginForm(request, data =request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request,user)

            return redirect('home')
    else:
        form = loginForm()
    return render(request,'Users/login.html',{'form':form})
@login_required
def account_view(request):
    if request.method == 'POST':
        form = accountForm(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            if password:
                user.set_password(password)
            user.save()
    else:
        form = accountForm(instance=request.user)

    countries = Country.objects.all()
    
    return render(request,'Users/account_base.html',{'form':form,'countries':countries})
@login_required
def myProduct_view(request):
    my_product = Product.objects.filter(
        user = request.user
    ).order_by('-created_at')
    for product in my_product:
        if product.images:
            try:
                product.image_list = json.loads(product.images)
            except json.JSONDecodeError:
                product.image_list = []
        else:
            product.image_list = []


    return render(request,'Users/myProduct.html',{'my_product':my_product})
def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def home(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request,'Users/index.html')

@login_required
def addAjax(request):
    if request.method == "GET":
        categories = Category.objects.all();

        brands = Brand.objects.all();

        return render(request,'Users/addProduct.html',{'categories':categories,'brands':brands})
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price' , '') 
        category_id = request.POST.get('category', '')
        brand_id = request.POST.get('brand', '')    
        sale_status = request.POST.get('sale_status', '') 
        sale = request.POST.get('sale', '0') 
        detail = request.POST.get('detail', '')

        files = request.FILES.getlist('images')

        error = {}

        if not name:
            error['name'] = 'tên sản phẩm không được để trống'

        if not price:
            error['price'] = ['Vui lòng nhập giá tiền']
        else:
            try:
                price_number = float(price)
                if price_number < 0:
                    error['price'] = ['Giá không được nhỏ hơn 0']
            except ValueError:
                error['price'] = ['Giá không hợp lệ']

        if not category_id:
            error['category'] = ['vui lòng chọn category']

        if not brand_id:
            error['brand'] = ['Vui lòng chọn brand']

        if sale_status not in ['0','1']:
            error['sale_status'] = ['Sale status không hợp lệ']

        if sale_status == '1':
            try:
                sale = int(sale)
                if sale < 0 or sale > 100:
                    error['sale'] = ['Giá sale phải từ 0-100']
            except ValueError:
                error['sale'] = ['Sale không hợp lệ']
        else:
            sale = 0

        if not files:
            error['images'] = ['Phải chọn ít nhất một ảnh']
        elif len(files) > 3 :
            error['images'] = ['Tối đa chỉ được upload 3 ảnh']
        else:
            for file in files:
                if file.content_type not in ['image/jpeg', 'image/jpg', 'image/png']:
                    error['images'] = f"{file.name} Không phải ảnh hợp lệ (jpg,png,jpeg)."
                    break
                if file.size > 1 * 1024 * 1024:
                    error ['images'] = f"{file.name} vượt quá 1MB"
                    break
        if error:
            return JsonResponse({'status': 'error', 'error': error}, status = 400)

        saved_filenames = []

        for file in files:
            filename = file.name.replace(" ","_")
            base, ext = os.path.splitext(filename)
            ext = ext.lower()

            #tạo đường lưu thư mục ảnh
            save_folder = os.path.join(settings.MEDIA_ROOT, "products")

            #tạo nếu chưa có thư mục
            os.makedirs(save_folder, exist_ok=True) 

            #tạo đường đẫn để lưu ảnh gốc
            original_path = os.path.join(save_folder,f"{base}{ext}")

            # Mở file ảnh gốc trong chế độ ghi nhị phân (wb+)
            # và ghi nội dung theo từng chunk để tránh lỗi với file lớn
            with open(original_path, "wb+") as dest :
                for chunk in file.chunks():
                    dest.write(chunk)

            #lưu tên file gốc vào dsach saved_names để sau này ghi vào csdl
            saved_filenames.append(f"{base}{ext}")

            #resize
            #Dùng pillow để mở ảnh vừa lưu
            img = Image.open(original_path)

            #Lặp qua 2 kích thước mong muốn : 100px và 400px
            for size in [100,200]:

                #copy ảnh gốc, tránh sửa ảnh gốc trực tiếp
                img_copy = img.copy()

                # Tạo thumbnail với kích thước giới hạn là size x size.
                # Nếu ảnh gốc là 800x600 và size=100,
                # ảnh sau cùng có thể là 100x75
                img_copy.thumbnail((size, size))
                resized_name = f"{size}_{base}{ext}"

                # Tạo đường dẫn cho ảnh thumbnail.
                resized_path = os.path.join(save_folder, resized_name)

                # Lưu ảnh thumbnail vào thư mục products.
                img_copy.save(resized_path, format=img.format)

        #check category và brand
        try:
            category = Category.objects.get(id=category_id)

            brand = Brand.objects.get(id= brand_id)

        except (
            Category.DoesNotExist,
            Brand.DoesNotExist
        ):
            return JsonResponse(
                {
                'status' : 'error',
                'error' : {'category hoặc brand không tồn tại'}
                },
                status = 400
            )


        #lưu DB
        Product.objects.create(
            user = request.user,
            name = name,
            price = price,
            category = category,
            brand = brand,
            sale_status = sale_status,
            sale = sale,
            images = json.dumps(saved_filenames),
            detail = detail
        )
        return JsonResponse({'status':'success',
            # 'redirect': reverse('my-product'),
            'message': 'Thêm sản phẩm thành công'
            })
    return JsonResponse({'error': 'Only POST allowed'}, status = 400)      

@login_required
def editProduct(request, product_id):
        
    try:
        product = Product.objects.get(id = product_id,user = request.user)
    except Product.DoesNotExist:
        return JsonResponse(
            {
                'error' : 'status',
                'message' : 'Không tìm thấy sản phẩm'
            },
            status = 400
        )
    if request.method == 'GET':
        categories = Category.objects.all()
        
        brands = Brand.objects.all()
        try:
            product.image_list = json.loads(
                product.images
            ) if product.images else []
        except (json.JSONDecodeError, TypeError):
            product.image_list = []
        return render(request,'Users/editProduct.html',{'product':product,'categories':categories,'brands':brands})

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price' , '') 
        category_id = request.POST.get('category', '')
        brand_id = request.POST.get('brand', '')    
        sale_status = request.POST.get('sale_status', '') 
        sale = request.POST.get('sale', '0') 
        detail = request.POST.get('detail', '')
        
        files = request.FILES.getlist('images')

        #Các ảnh cũ được chọn để xóa
        delete_images = request.POST.getlist('delete_images')
        
        error = {}

        #Lấy list ảnh cũ
        try:
            old_image = json.loads(product.images) if product.images else []
        except(json.JSONDecodeError,TypeError):
            old_image = []

        #check delete_images
        #Chỉ cho phép xóa những ảnh đang tồn tại
        delete_images = [
            image for image in delete_images
            if image in old_image 
        ]
        #tạo list ảnh cũ sau khi xóa
        remaining_image = []
        for image in old_image:
            if image not in delete_images:
                remaining_image.append(image)
        
        if not price:
                error['price'] = ['Vui lòng nhập giá tiền']
        else:
            try:
                price_number = float(price)
                if price_number < 0:
                    error['price'] = ['Giá không được nhỏ hơn 0']
            except ValueError:
                error['price'] = ['Giá không hợp lệ']

        if sale_status not in ['0','1']:
            error['sale_status'] = ['Sale status Không hợp lệ']

        if sale_status == '1':
            try:
                sale = int(sale)
                if sale < 0 or sale > 100:
                    error['sale'] = ['Giá phải từ 0-100']
            except:
                error['sale'] = ['sale không hợp lệ']
        else:
            sale = 0

        #check lại tổng số ảnh
        total_images = len(remaining_image) + len(files)
        if total_images > 3:
            error['images'] = [
                f'Sản phẩm chỉ được tối đa 3 ảnh. '
                f'Hiện tại có {len(remaining_image)} ảnh cũ và '
                f'bạn đang thêm {len(files)} ảnh mới.'
            ]
        
        for file in files:
            if file.content_type not in ['image/jpg','image/jpeg','image/png']:
                error['images'] = [f"{file.name} Không phải ảnh hợp lệ (jpg,png,jpeg)."]
                break
            if file.size > 1 * 1024 * 1024:
                error['images'] = [f"{file.name} quá 1MB"]
                break
        if error:
            return JsonResponse(
                {
                    'status' : 'error',
                    'error' : error
                },
                status = 400
            )

        
        try:
            category = Category.objects.get( id = category_id)

            brand = Brand.objects.get(id = brand_id)
        except(
            Category.DoesNotExist,
            Brand.DoesNotExist,
        ):
            return JsonResponse(
                {
                'status' : 'error',
                'error' : 'Category và Brand không tồn tại'
                },
            status = 400
            )
        # Xóa file ảnh cũ
        save_folder = os.path.join(settings.MEDIA_ROOT,'products')
        for image_name in delete_images:
            image_path = os.path.join(save_folder,image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
            # Xóa ảnh thumbnail 100 và 200
            thumb_100 = os.path.join(save_folder,f'100_{image_name}')
            if os.path.exists(thumb_100):
                os.remove(thumb_100)
            thumb_200 = os.path.join(save_folder,f'200_{image_name}')
            if os.path.exists(thumb_200):
                os.remove(thumb_200)
        new_image = []
        for file in files:
            filename = file.name.replace(' ','_')
            base, ext = os.path.splitext(filename)
            ext = ext.lower()
            save_folder = os.path.join(settings.MEDIA_ROOT,'products')

            os.makedirs(save_folder,exist_ok=True)
            original_path = os.path.join(save_folder,f'{base}{ext}')

            with open(original_path, 'wb+')as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            new_image.append(f'{base}{ext}')
            #Thumbnail
            img = Image.open(original_path)
            for size in [100,200]:
                img_copy = img.copy()
                img_copy.thumbnail(
                    (size,size)
                )
                resized_name = (f'{size}_{base}{ext}')

                resize_path = os.path.join(save_folder,resized_name)

                img_copy.save(resize_path)
        #Ghép ảnh cũ và ảnh mới lại
        final_images = (remaining_image+new_image)
        #reset KEY
        final_images = list(final_images)

        #UPDATE 
        product.name = name
        product.price = price
        product.category = category
        product.brand = brand
        product.sale = sale
        product.sale_status = sale_status
        product.detail = detail
        product.images = json.dumps(final_images)

        product.save()
        return JsonResponse(
            {
                'status': 'success',
                'message': 'Sửa sản phẩm thành công'
            }
        )
    return JsonResponse(
        {
            'status' : 'error',
            'error' : 'Only POST allowed'
        },
        status = 400
    )


