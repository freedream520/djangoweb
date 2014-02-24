$(function () {
    // 给评论按钮绑定click事件
    $("#submit-res-comment").bind("click", function () {
        var content = $("#res-comment-content").val();
        var res_id = $("div[id^='detail']").attr('id').split('-')[1];

        if (!content || content.length <= 0) {
            setErrorMsg("评论内容不能为空!");
            return;
        }
        if (content.length > 1000) {
            setErrorMsg("评论内容不能超过1000个字符!");
            return;
        }
        // TODO check res_id

        // 显示loading图片，并且按钮文案变成正在提交
        $('#submit-res-comment').button('loading');
        $('#submit-loading').css("display", "inline");

        $.post('/api/detail/' + res_id + '/add_new_comment/',
            {
                content: content
            },
            function (data, status) {
                data = JSON.parse(data);
                if (data.success == 0) {
                    // TODO add node, not refresh
                    window.location.reload()
                } else {
                    setErrorMsg(data.error_msg)
                }

            }).fail(function () {
                setErrorMsg('尼码， 服务器出现异常了，管理员赶紧过来看看！');
            }).always(function () {
                // reset status
                $('#submit-res-comment').button('reset');
                $('#submit-loading').css("display", "none");
            });
    });

    function setErrorMsg(msg) {
        $('#error-msg').text(msg).css('display', 'block');
    }
});


