$(function () {
    // 回到顶部插件
    $.scrollUp({
        scrollText: ''
    });
    // 点赞功能
    $('.vote-up').bind('click', function () {
        vote($(this), 'up');
        return false;
    });
    $('.vote-down').bind('click', function () {
        vote($(this), 'down');
        return false;
    });
});

function vote(node, action) {
    var self = node;
    var res_id = self.attr('id').split('-')[1];

    if (self.hasClass('vote-disabled') || self.hasClass('vote-enabled')) {
        // do nothing
        return;
    }
    $.get('/api/resource_vote/' + res_id + '/' + action + '/',
        function (result, status) {
            result = JSON.parse(result);
            if (result.success == 0) {
                cnt = self.children('span').text();
                self.children('span').text(parseInt(cnt) + 1);

                self.addClass('vote-enabled');
                action == "up" ? self.next().addClass('vote-disabled') : self.prev().addClass('vote-disabled')

            } else if (result.error_type = "require_login") {
                if ($('#require-login').length <= 0) {
                    $('body').append(require_login_modal());
                }
                $('#require-login').modal('show')
            }
        }).always(function () {
            self = null
        });
}


function initPaginator(curPage, pages, pageUrl) {
    var options = {
        currentPage: curPage,
        totalPages: pages,
        size: 'normal',
        alignment: 'center',
        itemContainerClass: function (type, page, current) {
            return (page === current) ? "active" : "pointer-cursor";
        },

        itemTexts: function (type, page, current) {
            switch (type) {
                case "first":
                    return "首页";
                case "prev":
                    return "<";
                case "next":
                    return ">";
                case "last":
                    return "最后一页";
                case "page":
                    return page;
            }
        },

        pageUrl: function (type, page, current) {
            return pageUrl + page;
        }
    };
    $('#pagination').bootstrapPaginator(options);
}

function require_login_modal() {
    return '<div id="require-login" class="modal hide fade"><div class="modal-header require-login-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button> <h4>需要登录</h4> </div> <div class="modal-body require-login-body "> <p>您必须登录后才能继续进行此操作</p> </div> <div class="modal-footer require-login-footer"> <button class="btn" data-dismiss="modal" aria-hidden="true">取消</button> <a class="btn btn-primary" href="/login/">转到登录页</a> </div> </div>';
}

