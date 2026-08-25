// $("form#productAjax").submit(function(e){
//     e.preventDefault();
    
//     const formData = new FormData(this);

//     $.ajax({
//         url:'/product/addAjax',
//         type : 'POST',
//         data : formData,
//         processData : false,
//         contentType : false,
//         headers : {
//             "X-CSRFToken": "{{ csrf_token }}"
//         },
//         success : function(data){
//             $('error-name').text(data.error.name|| '');
//             $('error-price').text(data.error.price || '');
//             $('error-images').text(data.error.images || '');
//         },
//         error : function(xhr) {
//             console.log(xhr.responseJSON);
//         }
//     })
// })
$(document).ready(function(){
    $("#sale_status").change(function(){
        if ($(this).val()== "1"){
            $("#sale-box").show()
        }
        else{
            $("#sale-box").hide();
            $("#sale").val(0)
        }
    });
    $("#productAjax").submit(function(e){
        e.preventDefault();

        //xoa loi cu
        $("#error").text("");
        $("#error-name").text("");
        $("#error-price").text("");
        $("#error-category").text("");
        $("#error-brand").text("");
        $("#error-sale-status").text("");
        $("#error-sale").text("");
        $("#error-images").text("");

        const formData = new FormData(this);

        $.ajax({
            url : "/Users/add-product/",
            type : "POST",
            data : formData,
            processData : false,
            contentType : false,

            success : function(data){
                if(data.status == "success"){
                    alert("Thêm sản phẩm thành công")
                    // window.location.href = data.redirect;
                    $("#productAjax")[0].reset();
                    $("#sale-box").hide();
                }
            },
            error : function(xhr){
                const data = xhr.responseJSON;

                if(!data){
                    return;
                }
                if(data.error){
                    $("#error-name").text(data.error.name || "");
                    $("#error-price").text(data.error.price || "");
                    $("#error-category").text(data.error.category || "");
                    $("#error-brand").text(data.error.brand || "");
                    $("#error-sale-status").text(data.error.sale_status || "");
                    $("#error-sale").text(data.error.sale || "")
                    $("#error-images").text(data.error.images || "");
                }
            }
        });
    });
});