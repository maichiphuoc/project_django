document.addEventListener('DOMContentLoaded', function () {

    console.log("===== COMMENT JS START =====");

    //form comment

    const commentData =
        document.getElementById('comment-data');

    const commentForm =
        document.getElementById('comment-form');


    console.log("commentData:", commentData);
    console.log("commentForm:", commentForm);


    // =========================
    // KIỂM TRA HTML
    // =========================

    if (!commentData) {
        console.error("KHÔNG TÌM THẤY comment-data");
        return;
    }

    if (!commentForm) {
        console.error("KHÔNG TÌM THẤY comment-form");
        return;
    }
    const commentUrl =
        commentData.dataset.commentUrl;


    console.log(
        "commentUrl:",
        commentUrl
    );



    commentForm.addEventListener('submit', function (e) {

        e.preventDefault();


        const isAuthenticated = commentData.dataset.authenticated === 'true';


        if (!isAuthenticated) {

            alert('Vui lòng login để comment');

            return;
        }


        //lấy data
        const blogId =
            document.getElementById('blog_id').value;


        const commentInput =
            document.getElementById('comment');


        const comment =
            commentInput.value.trim();


        const parentId =
            document.getElementById('parent_id').value;

        if (comment === '') {

            alert('Vui lòng nhập comment');

            return;
        }

        //csrf
        const csrfToken =
            document.querySelector(
                '[name="csrfmiddlewaretoken"]'
            ).value;
        //ajax
        fetch(commentUrl, {

            method: 'POST',

            headers: {

                'Content-Type':
                    'application/x-www-form-urlencoded',

                'X-CSRFToken':
                    csrfToken
            },

            body: new URLSearchParams({

                blog_id: blogId,

                comment: comment,

                parent_id: parentId

            })

        })


        // nhận response
        .then(response => response.json())


        .then(data => {

            //báo lỗi server
            if (!data.success) {

                alert(data.error);

                return;
            }


            // lấy comment server trả về
            const cmt = data.data;
            
            // tạo html comment
            const html = `

                <div
                    class="comment-item"
                    id="comment-${cmt.id}"
                >

                    <div class="comment-user">

                        <img
                            src="${cmt.author_image}"
                            width="50"
                            height="50"
                        >

                        <strong>
                            ${cmt.author_name}
                        </strong>

                    </div>


                    <div class="comment-content">

                        ${cmt.comment}

                    </div>


                    <div class="comment-time">

                        ${cmt.created}

                    </div>


                    <button
                        type="button"
                        class="reply-btn"
                        data-id="${cmt.id}"
                    >
                        Reply
                    </button>


                </div>

            `;
            //comment cha
            if (cmt.parent_id === null) {

                document
                    .getElementById('comments-list')
                    .insertAdjacentHTML(
                        'beforeend',
                        html
                    );

            }


            //comment con
            else {

                const parentElement =
                    document.getElementById(
                        `comment-${cmt.parent_id}`
                    );


                if (!parentElement) {

                    console.error(
                        'Không tìm thấy comment cha:',
                        cmt.parent_id
                    );

                    return;
                }


                let replies =
                    parentElement.querySelector(
                        '.replies'
                    );


                // Nếu comment cha chưa có .replies
                if (!replies) {

                    replies =
                        document.createElement('div');

                    replies.className = 'replies';

                    parentElement.appendChild(
                        replies
                    );
                }


                replies.insertAdjacentHTML(
                    'beforeend',
                    html
                );

            }


            // reset form
            commentInput.value = '';

            document.getElementById(
                'parent_id'
            ).value = '';

        })

        // tbao lỗi ajax
        .catch(error => {

            console.error(
                'AJAX ERROR:',
                error
            );

            alert(
                'Có lỗi xảy ra khi gửi comment'
            );

        });

    });


    // xử lí click reply

    document
        .getElementById('comments-list')
        .addEventListener('click', function (e) {

            if (
                e.target.classList.contains('reply-btn')
            ) {

                const commentId =
                    e.target.dataset.id;


                // Lưu ID comment cha
                document.getElementById(
                    'parent_id'
                ).value = commentId;


                // Focus vào textarea
                document.getElementById(
                    'comment'
                ).focus();

            }

        });

});