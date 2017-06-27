function initPage(divider)
{
    function initPageDiv()
    {
        $("div#pageDiv").css({
            "width": width / divider * (divider - 2.2),
            "height": $(document).height(),
            "left": width / divider * 1.6,
            "margin-right": width / divider,
        });
    }

    function navCss()
    {
        return {
            /*"width": width / divider,*/
            "height": height,
            "padding-top": height / 2,
        }
    }

    function initNav(elem)
    {
        if (elem != undefined) {
            elem.css(navCss());
            elem.css("cursor", "hand");
        }
    }

    width = $(window).width();
    height = $(window).height();
    /*
    initPageDiv();
    */
    initNav($("div#prevPage"));
    initNav($("div#nextPage"));
}

window.onload = function() {
    initPage(16);
}
