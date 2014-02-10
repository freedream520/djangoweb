$(function () {
	// 回到顶部插件
	$.scrollUp({
		scrollText: ''
	});
});

function initEvaluate() {
	$("a[id^='good']").bind('click', function() { 
		var self = $(this)
		var resid = self.attr('id').split('-')[1];
		$.get('/good/' + resid + '/', function(data, status){
			if (data === '1') {
				var good = self.children('span').text();
				self.children('span').text(parseInt(good) + 1);
			}
		});
		return false;
	});
	$("a[id^='bad']").bind('click', function() { 
		var self = $(this)
		var resid = self.attr('id').split('-')[1];
		$.get('/bad/' + resid + '/', function(data, status){
			if (data === '1') {
				var bad = self.children('span').text();
				self.children('span').text(parseInt(bad) + 1);
			}
		});
		return false;
	});
}

function initPaginator(curPage, pages, pageUrl) {
	var options = {
		currentPage: curPage,
		totalPages: pages,
		size:'normal',
		alignment:'center',
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

		pageUrl: function(type, page, current){
			return pageUrl + page;
		}
	}
	$('#pagination').bootstrapPaginator(options);
}

