$(function () {
    var attach_type = '';
    var attach_id = '';

    // 上传文件
    $('#fileupload').fileupload({
        dataType: 'json',
        add: function (e, data) {
            attach_type = 'image';
            attach_id = '';

            $('.upload-media').css("display", "block");
            $('#triangle').css("display", "none");
            $('.upload-media-container').css({"padding": "0px", "background-color": "rgb(255, 255, 255)", "border": "none"});
            $('#btn-file-url-cancel').css("display", "none");
            $('#url-input-box').css("display", "none");

            $('#preview-img-box').children().remove();
            $('#preview-img-box').append('<img id="loading-image" src="http://sharehp.qiniudn.com/share/loading.gif">');
            data.submit();
        },
        done: function (e, result) {
            result = JSON.parse(JSON.stringify(result.result));
            // 图片上传成功
            if (result.success == 0) {
                var src = result.data.src;
                attach_id = src;

                $('#preview-img-box').children().remove();
                $('#preview-img-box').append('<a id="btn-close-preview" class="btn-close-preview" href="###"></a>');
                $('#preview-img-box').append('<img id="tmp_image" style="border: 1px solid #EBE6DE;" width="200" height="80" src=/static/sharehp/tmp/' + src + ' >');

                // 取消图片事件
                $("#btn-close-preview").bind('click', function () {
                    attach_type = '';
                    attach_id = '';

                    $("#btn-close-preview").css("display", "none");
                    $('#preview-img-box').children().remove();
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
                })
            } else {
                $('#preview-img-box').children().remove();
                $('#error-msg').text(result.error_msg).css('display', 'block');
            }
        }
    });

    // 上传视频
    $('#add-video').bind('click', function () {
        attach_type = 'video';
        attach_id = '';

        $('.upload-media').css("display", "block");
        $('#triangle').css("display", "block").css("left", "95px");
        $('.upload-media-container').removeAttr('style');
        $('#btn-file-url-cancel').css("display", "inline");
        $('#url-input-box').css("display", "block");
        $('#preview-img-box').children().remove();
    });

    $('#btn-file-url-cancel').bind('click', function () {
        attach_type = '';
        attach_id = '';

        $('#preview-img-box').children().remove();
        $('.upload-media').css("display", "none");
    });

    // 提交视频
    $('#submit-video-url').bind('click', function () {
        video_url = $('#input-video-url').val();
        // check video_url
        if(!video_url) {
            $('#video-err-msg').text('请输入视频地址!');
            return;
        }
        if(video_url.lastIndexOf('http://www.56.com/', 0) !== 0) {
            $('#video-err-msg').text('对不起，你输入的视频地址暂时不支持!');
            return;
        }

        $("#url-input-box").css("display", "none");
        $('#preview-img-box').children().remove();
        $('#preview-img-box').append('<img id="loading-image" src="/static/sharehp/img/loading.gif">');
        $.post('/api/upload_video/',
            {
                url: video_url
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    data = result.data;
                    attach_id = data.id;

                    $('#preview-img-box').children().remove();
                    $('#preview-img-box').append('<img id="tmp_video" src=' + data.src + ' height="72" width="120">');
                    $('#preview-img-box').append('</p><a target="_blank" href=' + data.url + ' >' + data.title + '</a></div>'
                    )
                }else {
                    // 上传视频失败
                    $('#preview-img-box').children().remove();
                    $('#url-input-box').css("display", "block");
                    $('#video-err-msg').text(result.error_msg);
                }

            });
    });

    // 发布资源
    $('#submit-new-resource').bind('click', function () {
        title = $('#resource-title').val();
        if (!title|| title.length <= 0) {
            setErrorMsg("资源标题不能为空!");
            return;
        }
        if (title.length > 1000){
            setErrorMsg("资源标题不能超过1000个字符!");
            return;
        }

        $('#submit-new-resource').button('loading');
        $.post('/api/add_new_resource/',
            {
                title: title,
                type: attach_type,
                attach: attach_id
            },
            function (result, status) {
                result = JSON.parse(result);
                if (result.success == 0) {
                    window.location.href = '/index/'
                } else {
                    setErrorMsg(result.error_msg);
                }
                $('#submit-new-resource').button('reset');
            })
    });
    function setErrorMsg(msg){
        $('#error-msg').text(msg).css('display', 'block');
    }
});