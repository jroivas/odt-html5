function initPage(divider)
{
	width = $(window).width();
	height = $(window).height();
	$("div#pageDiv").css({
		"width": width/divider*(divider-2.2),
		"height": $(document).height(),
		"left": width/divider,
		"margin-right": width/divider,
	});

	prevpage = $("div#prevPage");
	if (prevpage!=undefined) {
		prevpage.css(
		{
			"width": width/divider,
			"height": height,
			"padding-top": height/2,
		});
		prevpage.click(function() {
			flipPrevPage();
		});
		prevpage.css("cursor","hand");
		prevpage.hover(function () {
		    $(this).css({"background-color": "#ddd"});
		  }, function() {
			var obj = {
				"background-color": "white"
			};
			$(this).css(obj);
		  });
	}

	nextpage = $("div#nextPage");
	if (nextpage!=undefined) {
		nextpage.css(
		{
			"width": width/divider,
			"height": height,
			"padding-top": height/2,
		});
		nextpage.click(function() {
			flipNextPage();
		});
		nextpage.css("cursor","hand");

		nextpage.hover(function () {
		    $(this).css({"background-color": "#ddd"});
		  }, function() {
			var obj = {
				"background-color": "white"
			};
			$(this).css(obj);
		  });
	}
}

window.onload = function() {
	initPage(16);
}

function switchPage(diff) {
	cpages=$(pagecnt).val()*1;
	page=$(pagenum).val()*1;
	npage=page+diff;
	if (npage>=1 && npage<=cpages) {
		$(pagenum).val(""+npage);
		$("div.pageNum"+page).css("display","none");
		$("div.pageNum"+npage).css("display","block");
	}
}

function toPrevPage() {
	switchPage(-1);
}

function toNextPage() {
	switchPage(1);
}
