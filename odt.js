function initPage()
{
    function navCss()
    {
        return {
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

    height = $(window).height();
    initNav($("div#prevPage"));
    initNav($("div#nextPage"));
}

window.onload = function() {
    initPage();
}
