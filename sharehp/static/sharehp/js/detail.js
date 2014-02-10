$(function () {
    setCommentEvent()
    setViewArrowsEvent()
});

function setCommentEvent() {
    // 为detail页面上的回复链接绑定click事件
    $(".comment-link").bind("click", function () {
        var media_body = $(this).parent().parent();
        var commentid = media_body.attr('id');
        var userid = media_body.children('a.comment-user').attr('id');
        var nickname = media_body.children('a.comment-user').text();
        // 添加回复文案
        $("#reply-span").remove();
        $("#comment-block").after('<span id="reply-span"><a id=' + userid + '-' + commentid + ' href="###" class="i-cancel" title="取消">✖</a> 回复 ' + nickname + '</span>');
        // 为回复文案绑定事件
        $("a.i-cancel").bind("click", function () {
            $("#reply-span").remove()
            return false;
        });
    });

    // 给评论按钮绑定click事件
    $("#submit-commit").bind("click", function () {
        var content = $("#comment-block").val()
        // 回复评论
        if ($("#reply-span").length > 0) {
            var reply = $('#reply-span').children('a').attr('id').split('-');
            var toid = reply[0];
            var commentid = reply[1];
            $.post('/api/reply/',
                {
                    commentid: commentid,
                    toid: toid,
                    content: content
                },
                function (data, status) {
                    data = JSON.parse(data);
                    if (data.success == 0) {
                        window.location.reload()
                    }
                });
        }
        // 评论资源
        else {
            var resid = $("div[id^='detail']").attr('id').split('-')[1]
            $.post("/api/comment/",
                {
                    resid: resid,
                    content: content
                },
                function (data, status) {
                    data = JSON.parse(data);
                    if (data.success == 0) {
                        window.location.reload()
                    }
                });
        }
    });
}

function setViewArrowsEvent() {
    $("div[id^='detail']").bind({
        "mouseover": function () {
            $("#pin_view_arrows").css("visibility", "visible")
        },
        "mouseout": function () {
            $("#pin_view_arrows").css("visibility", "hidden")
        }
    });
}

