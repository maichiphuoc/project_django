document.addEventListener('DOMContentLoaded',function(){
    const buttons = document.querySelectorAll('.btn-qty')

    buttons.forEach(function(button){
        button.addEventListener('click',function(event){
            event.preventDefault();

            const productId = this.dataset.id;

            const action = this.dataset.action;

            const csrfInput = document.querySelector(
                '[name=csrfmiddlewaretoken]'
            );

            if(!csrfInput){
                alert('Không tìm thấy token');
                return;
            }

            const csrfToken = csrfInput.value;

            //Ajax
            $.ajax({
                url: '/Users/cart/update/',
                type: 'POST',
                contentType : 'application/json',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                data : JSON.stringify({
                    product_id : productId,
                    action : action
                }),

                //ajax thành công
                success: function(response){
                    if(response.status !== 'success'){
                        alert(response.message ||'Có lỗi xảy ra');
                        return;
                    }

                    //Nếu sản phẩm bị xóa

                    if(response.delete == true){
                        const row = button.closest('tr');

                        if(row){
                            row.remove()
                        }
                    }

                    //Nếu chỉ thay đổi quantity
                    else{
                        const quantityElement = document.getElementById('quantity-' + productId);

                        if(quantityElement){
                            quantityElement.textContent = response.quantity;
                        }
                    }

                    //Cập nhật cart count header

                    const cartCount = document.getElementById('cart-count');

                    if(cartCount){
                        cartCount.textContent = response.cart_count;
                    }

                    const totalCount = document.getElementById('total-count');

                    if(totalCount){
                        totalCount.textContent = response.cart_count
                    }

                    //Nếu giỏ hàng đã trống

                    const tbody = document.querySelector('.info-cart table tbody');

                    if (response.cart_count ===0 ){
                        const infoCart = document.querySelector('.info-cart');
                        infoCart.innerHTML = `
                            <h2>Giỏ hàng của tôi</h2>

                            <p>Giỏ hàng đang trống</p>`;
                    }

                    
                },

                //Ajax thất bại
                error: function(xhr){
                    const response = xhr.responseJSON;

                    alert(response?.message ||'Có lỗi xảy ra');
                }
            });
        });
    });
});