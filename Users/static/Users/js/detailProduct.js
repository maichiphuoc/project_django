document.addEventListener('DOMContentLoaded', function () {

    const mainImg = document.getElementById('main-item');

    const thumbnails = document.querySelectorAll('.thumbnail-img');

    const imagePopup = document.getElementById('imagePopup');

    const popupImage = document.getElementById('popupImage');

    const closePopup = document.querySelector('.close-popup');


    //click sang ảnh nhỏ thì đổi sang ảnh lớn
    thumbnails.forEach(function(thumbnail){
        thumbnail.addEventListener('click',function(){
            const newSrc = this.getAttribute('src');
            //lấy ảnh nhỏ thành ảnh lớn
            mainImg.setAttribute('src',newSrc);

            //Xóa các active cũ
            document.querySelectorAll('.thumbnail-item').forEach(function(item){
                item.classList.remove('active');
            });
            //Active ảnh đang chọn
            this.parentElement.classList.add('active');
        });
    });

    //Click ảnh lớn thì popup lên
    if(mainImg){
        mainImg.addEventListener('click',function(){
            //lấy ảnh hiện tại
            popupImage.src = mainImg.src;
            //Hiển thị popup
            imagePopup.classList.add('show');

        });
    }

    //click vào x thì đóng popup
    if(closePopup){
        closePopup.addEventListener('click',function(){
            imagePopup.classList.remove('show')
        })
    }
    //click vào nền tối thì đóng popup
    imagePopup.addEventListener('click',function(event){
        if (event.target == imagePopup){
            imagePopup.classList.remove('show');
        }
    });

    //Bấm esc thì đóng popup

    document.addEventListener('keydown',function(event){
        if(event.key == 'Escape'){
            imagePopup.classList.remove('show');
        }
    });


    const addCartButton = document.getElementById('add-to-cart-btn');

    if (addCartButton) {

        addCartButton.addEventListener('click', function () {

            const productId = this.dataset.productId;

            const quantityInput = document.querySelector('.qty-input');

            let quantity = parseInt(quantityInput.value) || 1;

            if (quantity < 1) {
                quantity = 1;
                quantityInput.value = 1;
            }


            // Lấy CSRF token
            const csrfInput = document.querySelector(
                '[name=csrfmiddlewaretoken]'
            );

            if (!csrfInput) {

                console.error('Không tìm thấy CSRF Token');

                alert('Không tìm thấy CSRF Token');

                return;

            }

            const csrfToken = csrfInput.value;


            $.ajax({

                url: `/Users/add-to-cart/${productId}/`,

                type: 'POST',

                contentType: 'application/json',

                headers: {
                    'X-CSRFToken': csrfToken
                },

                data: JSON.stringify({
                    quantity: quantity
                }),

                success: function (response) {

                    console.log(response);

                    if (response.status === 'success') {
                        const cartCount = document.getElementById('cart-count');

                        if (cartCount) {

                            cartCount.textContent = response.cart_count;

                        }

                        alert(
                            'Đã thêm sản phẩm: ' +
                            response.product.name +
                            '\nSố lượng: ' +
                            response.product.quantity
                        );

                    }

                },

                error: function (xhr) {

                    console.log(xhr);

                    const response = xhr.responseJSON;

                    alert(
                        response?.message ||
                        'Có lỗi xảy ra'
                    );

                }

            });

        });

    }
});
