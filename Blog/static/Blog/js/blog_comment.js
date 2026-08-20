document.addEventListener('DOMContentLoaded', function () {


    const commentData =
        document.getElementById('comment-data');

    const commentForm =
        document.getElementById('comment-form');

    const commentsList =
        document.getElementById('comments-list');


    // ktra html

    if (!commentData || !commentForm || !commentsList) {
        return;
    }

    // url ajax

    const commentUrl =
        commentData.dataset.commentUrl;



    function checkLogin() {

        const isAuthenticated =
            commentData.dataset.authenticated === 'true';


        if (!isAuthenticated) {

            alert(
                'Vui lòng đăng nhập để comment'
            );

            return false;
        }


        return true;
    }


    // form comment cha

    commentForm.addEventListener(
        'submit',
        function (e) {

            e.preventDefault();

            if(! checkLogin){
                return;
            }


            // lấy blog id
            const blogId =
                document.getElementById(
                    'blog_id'
                ).value;


            // lấy nội dung comment
            const commentInput =
                document.getElementById(
                    'comment'
                );


            const comment =
                commentInput.value.trim();


            // kiểm tra rỗng
            if (comment === '') {

                alert(
                    'Vui lòng nhập comment'
                );

                return;
            }
            //Comment cha không có parent, parent_id = ''

            sendComment(
                blogId,
                comment,
                '',
                null
            );

        }
    );

    // hàm gửi comment ajax

    function sendComment(
        blogId,
        comment,
        parentId,
        replyFormContainer
    ) {

        // lấy CSRF
        const csrfToken =
            document.querySelector(
                '[name="csrfmiddlewaretoken"]'
            ).value;


        fetch(
            commentUrl,
            {

                method: 'POST',

                headers: {

                    'Content-Type':
                        'application/x-www-form-urlencoded',

                    'X-CSRFToken':
                        csrfToken

                },

                body:
                    new URLSearchParams({

                        blog_id: blogId,

                        comment: comment,

                        parent_id: parentId

                    })

            }
        )
        // nhận response

        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    'HTTP Error: ' +
                    response.status
                );

            }

            return response.json();

        })


        // xử lí data

        .then(function (data) {

            if (!data.success) {

                alert(data.error);

                return;
            }


            /*
                Comment server vừa tạo
            */

            const cmt = data.data;


            /*
                Tạo HTML
            */

            const html =
                createCommentHTML(cmt);

            // comment cha

            if (cmt.parent_id === null) {

                const commentList =
                    document.querySelector(
                        '.comment-list'
                    );


                commentList.insertAdjacentHTML(
                    'beforeend',
                    html
                );


                // xóa textarea comment cha

                document.getElementById(
                    'comment'
                ).value = '';

            }

            // comment con

            else {
                // tìm comment cha
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


                /*
                    Tìm ul.replies
                    trực tiếp của comment cha
                */

                let replies =
                    parentElement.querySelector(
                        ':scope > .replies'
                    );


                // nếu chưa có reply thì tạo

                if (!replies) {

                    replies =
                        document.createElement(
                            'ul'
                        );

                    replies.className =
                        'replies';

                    parentElement.appendChild(
                        replies
                    );

                }

                // thêm reply vào cuối dsach reply

                replies.insertAdjacentHTML(
                    'beforeend',
                    html
                );


                // xóa form reply

                if (replyFormContainer) {

                    replyFormContainer.innerHTML =
                        '';

                }

            }

        })


        //bắt lỗi ajax error

        .catch(function (error) {

            console.error(
                'AJAX ERROR:',
                error
            );

            alert(
                'Có lỗi xảy ra khi gửi comment'
            );

        });

    }


    // tạo html comment

    function createCommentHTML(cmt) {

        /*
            Nếu parent_id = null
            => comment cha

            Nếu có parent_id
            => comment con
        */


        if (cmt.parent_id === null) {

            return `

                <li
                    class="comment-item"
                    id="comment-${cmt.id}"
                >

                    <div class="comment-parent">

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


                    <div
                        class="reply-form-container"
                    ></div>


                    <ul class="replies"></ul>

                </li>

            `;

        }


        // comment con

        return `

            <li
                class="comment-child"
                id="comment-${cmt.id}"
            >

                <div class="comment-user">

                    <img
                        src="${cmt.author_image}"
                        width="40"
                        height="40"
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

            </li>

        `;

    }

    // click reply

    commentsList.addEventListener(
        'click',
        function (e) {


            // ktra có click vào nút reply không

            if (
                !e.target.classList.contains(
                    'reply-btn'
                )
            ) {

                return;
            }


            /*
                Kiểm tra login
            */

            if (!checkLogin()) {

                return;
            }


            // lấy id comment cha

            const commentId =
                e.target.dataset.id;


            // tìm thẻ li của comment cha

            const parentElement =
                document.getElementById(
                    `comment-${commentId}`
                );

            // tìm nơi đặt form

            const formContainer =
                parentElement.querySelector(
                    ':scope > .reply-form-container'
                );

            // nếu form đang mở thì đóng form

            if (
                formContainer.innerHTML.trim()
                !== ''
            ) {

                formContainer.innerHTML =
                    '';

                return;

            }

            // tạo form reply
            formContainer.innerHTML = `

                <form class="reply-form">

                    <textarea
                        class="reply-input"
                        placeholder="Viết câu trả lời..."
                    ></textarea>


                    <button
                        type="submit"
                        class="send-reply-btn"
                    >
                        Gửi reply
                    </button>


                    <button
                        type="button"
                        class="cancel-reply-btn"
                    >
                        Hủy
                    </button>

                </form>

            `;

            // focus textarea
            const replyInput =
                formContainer.querySelector(
                    '.reply-input'
                );

            replyInput.focus();


            // submit form reply
            const replyForm =
                formContainer.querySelector(
                    '.reply-form'
                );


            replyForm.addEventListener(
                'submit',
                function (event) {

                    event.preventDefault();


                    const reply =
                        replyInput.value.trim();


                    if (reply === '') {

                        alert(
                            'Vui lòng nhập nội dung reply'
                        );

                        return;
                    }


                    const blogId =
                        document.getElementById(
                            'blog_id'
                        ).value;


                    /*
                        parentId chính là
                        ID của comment cha
                    */

                    sendComment(
                        blogId,
                        reply,
                        commentId,
                        formContainer
                    );

                }
            );


            // button hủy
            const cancelButton =
                formContainer.querySelector(
                    '.cancel-reply-btn'
                );


            cancelButton.addEventListener(
                'click',
                function () {

                    formContainer.innerHTML =
                        '';

                }
            );

        }
    );

});