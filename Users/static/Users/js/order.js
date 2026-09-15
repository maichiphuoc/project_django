document.addEventListener("DOMContentLoaded" ,function(){
    const orderBtn = document.getElementById("order-btn")
    const checkoutForm = document.getElementById("checkout-form")

    if(!orderBtn || !checkoutForm){
        return;

    }

    orderBtn.addEventListener("click",function(){
        const formData  = new FormData(checkoutForm);

        //xac dinh day la hanh dong order
        formData.append("action","order");
        

        fetch(window.location.href, {
            method : "POST",
            body: formData,
            headers: {
                "X-Requested-With":"XMLHttpRequest"
            }

        })
        

        .then(response => response.json())
        .then(data =>{
            if(data.success){
                alert(data.message);

                //Xoa noi dung bang gio hang
                const cartInfo = document.querySelector(".info-cart");

                if(cartInfo){
                    cartInfo.innerHTML = `
                        <h2>Giỏ hàng của tôi</h2>
                        <p>Giỏ hàng đang trống</p>
                    `;
                }
            }
            else{
                alert(data.message);
            }
        })
        .catch(error =>{
            alert("Có lỗi khi xảy ra đặt hàng");
        });
        
    });
});