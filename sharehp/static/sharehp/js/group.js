$(function () {
    $('#fileupload').fileupload({
        dataType: 'json',
        add: function (e, data) {
            $('#preview-img-box').children('img').remove();
            $('#preview-img-box').append('<img id="loading-image" style="border: 1px solid #EBE6DE;" src="/static/sharehp/img/loading.gif">');
            data.submit();
        },
        done: function (e, result) {
            var result = JSON.parse(JSON.stringify(result.result))
            // 图片上传成功 FIXME
            if (result.success == 0) {
                var src = result.data.src;
                $('#preview-img-box').children('img').remove();
                $('#preview-img-box').append('<img id="tmp_image" style="border: 1px solid #EBE6DE;" width="200" height="80" src=/static/sharehp/tmp/' + src + ' >');
                // 预览事件
                $("#preview-img-box").bind({
                    "mouseover": function () {
                        $("#btn-close-preview").css("display", "inline")
                    },
                    "mouseout": function () {
                        $("#btn-close-preview").css("display", "none")
                    }
                })
            } else {
            }
        }
    });

    // 取消预览图片事件
    $("#btn-close-preview").bind('click', function () {
        $('#preview-img-box').children('img').remove()
        $("#btn-close-preview").css("display", "none")
        return false;
    });

    // 发帖按钮事件
    $('#add-new-topic').bind('click', function () {
        // 获取发帖的标题&内容
        var title = $('#topic-title').val();
        var content = $('#topic-content').val();
        if (!content || !title || content.length <= 0 || title.length <= 0) {
            // FIXME
        }
        // 获取小组ID FIXME
        var group_id = $("div[id^='group-id']").attr('id').split('-')[2];
        // 获取图片（可选）
        var image = '';
        if ($('#tmp_image').length > 0) {
            var src = $('#tmp_image').attr('src').split('\/');
            image = src[src.length - 1];
        }
        // 提交表单
        $.post('/api/group/' + group_id + '/add_new_topic/',
            {
                attachment: image,
                type: 'image', // FIXME
                title: title,
                content: content
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    window.location.href = '/group/' + group_id + '/'
                } else if (result.success == -1) {
                    // 标题校验失败
                    $('#topic-title').before('<span class="text-error">' + result.error_msg + '</span>')

                } else if (result.success == -2) {
                    // 内容校验失败
                    $('#topic-content').before('<span class="text-error">' + result.error_msg + '</span>');
                }
            });
    });

    // 回帖按钮事件
    $('#topic-comment-save').bind('click', function () {
        // 获取回复的内容并替换空格和换行符
        var content = $('#topic-comment-content').val();
        if (!content || content.length <= 0) {
            // FIXME
        }
        // var reg = new RegExp("\n","g");
        //content = content.replace(reg, "<br>");
        // 获取回复帖子的ID FIXME
        var topic_id = $("h4[id^='topic-id']").attr('id').split('-')[2];
        // 获取图片（可选）
        var image = '';
        if ($('#tmp_image').length > 0) {
            var src = $('#tmp_image').attr('src').split('\/');
            image = src[src.length - 1];
        }
        // 提交表单
        $.post('/api/group/topic/' + topic_id + '/add_new_comment/',
            {
                attachment: image,
                type: 'image', // FIXME
                content: content
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    window.location.reload();
                }
            });
    });

});

