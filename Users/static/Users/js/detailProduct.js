document.addEventListener('DOMContentLoaded', function () {

    const mainImg = document.getElementById('main-item');

    const thumbnails = document.querySelectorAll('.thumbnail-img');

    const imagePopup = document.getElementById('imagePopup');

    const popupImage = document.getElementById('popupImage');

    const closePopup = document.querySelector('.close-popup');


    // click ảnh nhỏ thì đổi sang ảnh lớn

    thumbnails.forEach(function (thumbnail) {

        thumbnail.addEventListener('click', function () {

            const newSrc = this.getAttribute('src');

            // Đổi ảnh lớn
            mainImg.setAttribute('src', newSrc);


            // Xóa active tất cả ảnh
            document.querySelectorAll('.thumbnail-item').forEach(function (item) {

                item.classList.remove('active');

            });


            // Active ảnh đang chọn
            this.parentElement.classList.add('active');

        });

    });


    // Khi click ảnh lớn thì mở popup

    if (mainImg) {

        mainImg.addEventListener('click', function () {

            // Lấy ảnh hiện tại
            popupImage.src = mainImg.src;

            // Hiển thị popup
            imagePopup.classList.add('show');

        });

    }


    // click x thì đóng popup

    if (closePopup) {

        closePopup.addEventListener('click', function () {

            imagePopup.classList.remove('show');

        });

    }


    // click nền tối thì đóng popup

    imagePopup.addEventListener('click', function (event) {

        if (event.target === imagePopup) {

            imagePopup.classList.remove('show');

        }

    });

    // bấm esc thì đóng popup

    document.addEventListener('keydown', function (event) {

        if (event.key === 'Escape') {

            imagePopup.classList.remove('show');

        }

    });

});