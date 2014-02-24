$(function () {
    var attach_id = '';

    $('#fileupload').fileupload({
        dataType: 'json',
        add: function (e, data) {
            // 清空之前所有预览信息
            $('#preview-img-box').children().remove();
            // 显示loading图片
            $('#preview-img-box').append('<img id="loading-image" src="http://sharehp.qiniudn.com/share/loading.gif">');
            data.submit();
        },
        done: function (e, result) {
            result = JSON.parse(JSON.stringify(result.result));
            // 图片上传成功
            if (result.success == 0) {
                var src = result.data.src;
                attach_id = src;
                // 移除loading
                $('#preview-img-box').children().remove();
                // 添加预览信息: x按钮
                $('#preview-img-box').append('<a id="btn-close-preview" class="btn-close-preview" href="###"></a>');
                // 添加预览信息: 图片 FIXME 临时目录
                $('#preview-img-box').append('<img id="tmp_upload_image" style="border: 1px solid #EBE6DE;" width="200" height="80" src=/static/sharehp/tmp/' + src + ' >');

                // 设置x按钮事件
                $("#btn-close-preview").bind('click', function () {
                    attach_id = '';
                    $('#preview-img-box').children().remove();
                    //$("#btn-close-preview").css("display", "none");
                    return false;
                });
                // 预览事件
                $("#preview-img-box").bind({
                    "mouseover": function () {
                        $("#btn-close-preview").css("display", "inline")
                    },
                    "mouseout": function () {
                        $("#btn-close-preview").css("display", "none")
                    }
                });
            } else {
                // 图片上传失败处理
                $('#preview-img-box').children().remove();
                $('#error-msg').text(result.error_msg).css('display', 'block');
            }
        }
    });


    // 设置发帖按钮事件
    $('#add-new-topic').bind('click', function () {
        // 获取发帖的标题&内容
        var title = $('#topic-title').val();
        var content = $('#topic-content').val();
        if (!title || title.length <= 0) {
            setErrorMsg("话题不能为空!");
            return;
        }
        if (title.length > 256) {
            setErrorMsg("话题不能超过256个字符!");
            return;
        }
        if (!content || content.length <= 0) {
            setErrorMsg("内容不能为空!");
            return;
        }
        if (content.length > 10000) {
            setErrorMsg("内容不能超过10000个字符!");
            return;
        }
        // 获取小组ID
        var group_id = $("div[id^='group-id']").attr('id').split('-')[2];

        // loading status
        $('#add-new-topic').button('loading');
        $('#submit-loading').css("display", "inline");

        // 提交表单
        $.post('/api/group/' + group_id + '/add_new_topic/',
            {
                attach: attach_id,
                type: 'image', // TODO video
                title: title,
                content: content,
                has_attach: attach_id == '' ? 'false' : 'true'
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    window.location.href = '/group/' + group_id + '/'
                } else {
                    setErrorMsg(result.error_msg);
                }

            }).fail(function () {
                setErrorMsg('尼码， 服务器出现异常了，管理员赶紧过来看看！');
            }).always(function () {
                // reset status
                $('#add-new-topic').button('reset');
                $('#submit-loading').css("display", "none");
            });
    });

    // 回帖按钮事件
    $('#topic-comment-save').bind('click', function () {
        var content = $('#topic-comment-content').val();
        if (!content || content.length <= 0) {
            setErrorMsg("内容不能为空!");
            return;
        }
        if (content.length > 10000) {
            setErrorMsg("内容不能超过10000个字符!");
            return;
        }
        // 获取回复帖子的ID
        var topic_id = $("h4[id^='topic-id']").attr('id').split('-')[2];

        // loading status
        $('#topic-comment-save').button('loading');
        $('#submit-loading').css("display", "inline");

        // 提交表单
        $.post('/api/group/topic/' + topic_id + '/add_new_comment/',
            {
                attach: attach_id,
                type: 'image', // TODO video
                content: content,
                has_attach: attach_id == '' ? 'false' : 'true'
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    window.location.reload();
                } else {
                    setErrorMsg(result.error_msg);
                }
                /**
                 $('#comment-success').modal('show');
                 setTimeout(function () {
                        $('#comment-success').modal('hide');
                        window.location.reload();
                    }, 900)
                 */
            }).fail(function () {
                setErrorMsg('尼码， 服务器出现异常了，管理员赶紧过来看看！');
            }).always(function () {
                // reset status
                $('#topic-comment-save').button('reset');
                $('#submit-loading').css("display", "none");
            });
    });

    function setErrorMsg(msg) {
        $('#error-msg').text(msg).css('display', 'block');
    }
});

