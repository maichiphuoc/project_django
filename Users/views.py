import os
import json
from django.urls import reverse
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import registerForm,loginForm, accountForm
from .models import Country,Product,Category,Brand,Cart,CartItem,Order_history,OrderItem
from django.conf import settings
from django.contrib.auth.hashers import make_password
from PIL import Image

#email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


#ajax
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse

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

            send_welcome_email(user)

            # return HttpResponse("Đăng kí thành công, Đã gửi mail")

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

def send_welcome_email(user):
    subject = 'Chào mừng bạn đến với website'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    #nội dung text callback
    text_content = f"Chào {user.username}, cảm ơn bạn đã đăng kí"

    #render html từ template
    html_content = render_to_string('Users/emails/welcome_email.html',{'user':user})

    #gửi email
    msg = EmailMultiAlternatives(subject,text_content, from_email,to )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def confirmation_order_email(
    user,
    order,
    order_items,
    cart_count,
    cart_total,
    shopper_phone,
    bill_company,
    bill_email,
    bill_title,
    bill_first_name,
    bill_last_name,
    bill_address,
    shipping_notes,
    ship_to_bill
):
    subject = 'Xác nhận đơn hàng website'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    context = {

        'user': user,

        'order': order,

        'order_items': order_items,

        'cart_count': cart_count,

        'cart_total': cart_total,

        'shopper_phone': shopper_phone,

        'bill_company': bill_company,

        'bill_email': bill_email,

        'bill_title': bill_title,

        'bill_first_name': bill_first_name,

        'bill_last_name': bill_last_name,

        'bill_address': bill_address,

        'shipping_notes': shipping_notes,

        'ship_to_bill': ship_to_bill,

    }

    html_content = render_to_string('Users/emails/confirm_purchase_email.html',context)

    msg = EmailMultiAlternatives(subject,'',from_email,to )
    msg.attach_alternative(html_content,"text/html")
    msg.send()

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
    products = Product.objects.all().order_by('-created_at')[:6]
    for product in products:
        try:
            product.image_list = json.loads(product.images) if product.images else []
        except(json.JSONDecodeError,TypeError):
            product.image_list = []

    return render(request,'Users/index.html',{'products':products})

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
@login_required
def detailProduct(request, product_id):
    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist:
        return JsonResponse(
            {
                'error' : 'status',
                'message' : 'Không tìm thấy sản phẩm'
            },
            status = 400
        )
    
    try:
        product.image_list = (json.loads(product.images) if product.images else [])
    except(json.JSONDecodeError, TypeError):
        product.image_list = []
    return render(request,'Users/detail_Product.html',{'product':product})

@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return JsonResponse(
            {
                'status':'error',
                'message':'Chỉ cho phép POST'
            },
            status = 400
        )
    try:
        data = json.loads(request.body)

        
        quantity = int(data.get('quantity',1))
        if quantity <1:
            quantity = 1

        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist:
        return JsonResponse(
        {
            'error':'status',
            'message':'Không tìm thấy sản phẩm'
        },
        status = 400
    )
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse(
            {
                'status':'error',
                'message':'Dữ liệu không hợp lệ'
            },
            status = 400
        )

    cart, created = Cart.objects.get_or_create(
        user = request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart = cart,
            product = product,
            defaults={
                'quantity':quantity
            }
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save(update_fields=['quantity'])

    cart_count = sum(
        item.quantity
        for item in cart.items.all()
    )
    return JsonResponse(
        {
            'status': 'success',
            'message': 'Đã lấy thông tin sản phẩm',
            'cart_count':cart_count,

            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'sale': product.sale,
                'sale_status' : product.sale_status,
                'image' : product.images,
                'quantity': quantity
            }
        }
    )

@login_required
def cart_view(request):
    
        cart, created = Cart.objects.get_or_create(
            user = request.user
        )

        cart_items = CartItem.objects.filter(
            cart = cart,
        ).select_related(
            'product'
        )
        for item in cart_items:
            try:
                item.product.image_list = (json.loads(item.product.images)
                    if item.product.images
                    else [])
            except(json.JSONDecodeError, TypeError):
                item.product.image_list = []
        return render(request,'Users/my_cart.html',{'cart':cart,'cart_items':cart_items})
@login_required
def update_cart(request):
    if request.method != 'POST':
        return JsonResponse(
            {
                'status':'error',
                'message':'Chỉ cho phép POST',
            },
            status = 400
        )
    try:
        data = json.loads(request.body)

        product_id = int(data.get('product_id'))

        action = data.get('action')

    except (json.JSONDecodeError,ValueError, TypeError):
        return JsonResponse(
            {
                'status':'error',
                'message':'Dữ liệu không hợp lệ'
            },
            status = 400,
        )
    #kiểm tra aciton
    if action not in ['plus','minus','delete']:
        return JsonResponse(
            {
                'status':'error',
                'message':'Action không hợp lệ'
            },
            status = 400,
        )
    try:
        cart = Cart.objects.get(
            user = request.user
        )
    except(json.JSONDecodeError, TypeError):
        return JsonResponse(
            {
                'status':'error',
                'message':'Không tìm thấy sản phẩm'
            },
            status = 400,
        )

    try:
        cart_item = CartItem.objects.get(
            cart = cart,
            product_id = product_id
        )
    except CartItem.DoesNotExist:
        return JsonResponse(
            {
                'status':'error',
                'message':'Sản phẩm không có trong giỏ hàng'
            },
            status = 400,
        )

    if action == 'plus':
        cart_item.quantity +=1
        cart_item.save()

    elif action == 'minus':
        cart_item.quantity -=1
        if cart_item.quantity <= 0:
            cart_item.delete()

            cart_count = sum(
                item.quantity
                for item in cart.items.all()
            )
            return JsonResponse(
                {
                    'status': 'success',

                    'message': 'Đã xóa sản phẩm',

                    'delete': True,

                    'cart_count': cart_count
                }
            )
        cart_item.save()
    
    elif action == 'delete':
        cart_item.delete()

        cart_count = sum(
            item.quantity
            for item in cart.items.all()
        )

        return JsonResponse(
            {
                'status':'success',
                'message':'Đã xóa sản phẩm',
                'delete': True,
                'quantity': 0,
                'cart_count' : cart_count
            }
        )

    cart_count = sum(
        item.quantity
        for item in cart.items.all()
    )

    return JsonResponse(
        {
            'status':'success',
            'message':'Cập nhật thành công',
            'delete':False,
            'quantity':cart_item.quantity,
            'cart_count':cart_count
        }
    )

def checkout(request):

    form = registerForm()

    cart = None
    cart_items = []

    
    cart_total = 0
    cart_count = 0
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register' and not request.user.is_authenticated:
            form = registerForm(request.POST,request.FILES)
            if form.is_valid():
                user = form.save(commit=False)

                user.set_password(form.cleaned_data['password'])
                user.is_superuser = False
                user.is_staff = False

                user.save()

                send_welcome_email(user)
                return redirect('login')
        elif action == 'order' and request.user.is_authenticated:

            shopper_name = request.POST.get('shopper_name','').strip()

            shopper_email = request.POST.get('shopper_email','').strip()

            shopper_phone = request.POST.get('shopper_phone','').strip()

            bill_company = request.POST.get(
                'bill_company',
                ''
            ).strip()

            bill_email = request.POST.get(
                'bill_email',
                ''
            ).strip()

            bill_title = request.POST.get(
                'bill_title',
                ''
            ).strip()

            bill_first_name = request.POST.get(
                'bill_first_name',
                ''
            ).strip()

            bill_last_name = request.POST.get(
                'bill_last_name',
                ''
            ).strip()

            bill_address = request.POST.get(
                'bill_address',
                ''
            ).strip()


            shipping_notes = request.POST.get(
                'shipping_notes',
                ''
            ).strip()

            ship_to_bill = request.POST.get(
                'ship_to_bill'
            ) == 'on'

            if not shopper_email:
                return JsonResponse(
                    {
                        'success':False,
                        'message':'Vui lòng nhập Email'
                    }
                )
            if shopper_email.lower() != request.user.email.lower():
                return JsonResponse(
                    {
                        'success':False,
                        'message':'Email phải trùng với email đăng kí'
                    }
                )

            #lấy Cart
            cart = Cart.objects.filter(
                user = request.user
            ).first()
            if not cart:
                return JsonResponse(
                    {
                        'success':False,
                        'message':'Giỏ hàng đang trống'
                    }
                )
            #Lấy CartIem
            cart_items = CartItem.objects.filter(
                cart=cart,
            ).select_related(
                'product'
            )
            if not cart_items.exists():
                return JsonResponse(
                    {
                        'success':False,
                        'message':'Giỏ hàng đang trống'
                    }
                )
            if not shopper_name:
                shopper_name = (
                    f'{request.user.first_name} '
                    f'{request.user.last_name}'
                ).strip()

                if not shopper_name:
                    shopper_name = request.user.username
            #Tính tổng tiền
            cart_total = 0
            cart_count = 0
            for item in cart_items:
                product = item.product
                price = item.product.price
                sale = product.sale if product.sale_status == 1 else 0

                item_total = (
                    item.quantity * price
                )

                discount = (
                    item_total * sale / 100
                )
                cart_total += (
                    item_total - discount
                )

                cart_count += item.quantity

            #Tạo order history
            order = Order_history.objects.create(
                user = request.user,
                name = shopper_name,
                email = shopper_email,
                phone = shopper_phone,
                total_price = cart_total
            )

            #Tạo order items
            for item in cart_items:
                product = item.product
                sale = (
                    product.sale
                    if product.sale_status == 1
                    else 0
                )
                OrderItem.objects.create(
                    order=order,

                    product=product,

                    price=product.price,

                    sale=sale,

                    quantity=item.quantity
                )
            #Lấy order items
            order_items = order.items.select_related(
                'product',
                'product__category',
                'product__brand'
            )
            #gửi mail xác nhận đến user
            confirmation_order_email(

                user=request.user,

                order=order,

                order_items=order_items,

                cart_count=cart_count,

                cart_total=cart_total,

                shopper_phone=shopper_phone,

                bill_company=bill_company,

                bill_email=bill_email,

                bill_title=bill_title,

                bill_first_name=bill_first_name,

                bill_last_name=bill_last_name,

                bill_address=bill_address,

                shipping_notes=shipping_notes,

                ship_to_bill=ship_to_bill

            )

            #Xóa sản phẩm khỏi giỏ
            cart_items.delete()


            #Trả json cho ajax
            return JsonResponse(
                {
                    'success':True,
                    'message':'Đặt hàng thành công',
                    'order_id':order.id,
                    'cart_count': 0,
                    'cart_total' : 0
                }
            )
    

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
                    user = request.user
                )
        
        cart_items = CartItem.objects.filter(
                    cart = cart,
                ).select_related(
                    'product'
                )
        for item in cart_items:
            try:
                item.product.image_list = (json.loads(item.product.images)
                    if item.product.images
                    else [])
            except(json.JSONDecodeError, TypeError):
                        item.product.image_list = []
        cart_count = sum(
            item.quantity
            for item in cart_items
        )
        cart_total = sum(
            (item.quantity * item.product.price) - (item.quantity * item.product.price) * (item.product.sale)/100
            for item in cart_items
        )


    return render(request,'Users/checkout.html',{'form':form,'cart_items':cart_items,'cart':cart,'cart_total': cart_total,'cart_count':cart_count})
