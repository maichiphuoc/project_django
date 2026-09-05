$(document).ready(function(){
    $('#sale_status').change(function(){
        if ($(this).val() == "1" ){
            $('#sale-box').show()
        } else{
            $('#sale-box').hide()
            $('#sale').val(0)
        }
    });
    $('#edit_productAjax').submit(function(e){
        e.preventDefault();
        let form = this;
        let formData = new FormData(form);

        $('#error-images').text('');

        $.ajax({
            url: window.location.href,
            type : 'POST',
            data : formData,
            processData : false,
            contentType : false,
            success : function(response){
                if(response.status == 'success'){
                    alert(response.message);
                    window.location.href = '/Users/my-product/';
                }
            },
            error : function(xhr) {
                let response = xhr.responseJSON;
                if(
                    response &&
                    response.error
                ){
                    let errors = response.error;
                    if(errors.images){
                        let message = Array.isArray(errors.images)
                            ? errors.images.join(' ')
                            : errors.images;
                        
                        $('#error-images').text(message);
                    }
                }else {
                    $('#error-images').text(
                        'Có lỗi xảy ra, vui lòng thử lại.'
                    );
                }
            }
        })
        
    })
})