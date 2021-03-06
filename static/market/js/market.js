$(function () {

    var index = $.cookie('index')
    console.log(index)
    if (index) {
        $('.type-slider li').eq(index).addClass('active')
    } else {
        $('.type-slider li:first').addClass('active')
    }


    $('.type-slider li').click(function () {

        $.cookie('index', $(this).index(), {expires: 3, path: '/'})
    })


    var categoryShow = false
    $('#category-bt').click(function () {

        categoryShow = !categoryShow
        categoryShow ? categoryViewShow() : categoryViewHide()


    })

    function categoryViewShow() {
        $('.category-view').show()
        $('#category-bt i').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down')

        sortViewHide()
        sortShow = false
    }

    function categoryViewHide() {
        $('.category-view').hide()
        $('#category-bt i').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
    }


    var sortShow = false
    $('#sort-bt').click(function () {
        sortShow = !sortShow
        sortShow ? sortViewShow() : sortViewHide()


    })

    function sortViewShow() {
        $('.sort-view').show()
        $('#sort-bt i').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down')

        categoryViewHide()
        categoryShow = false
    }

    function sortViewHide() {
        $('.sort-view').hide()
        $('#sort-bt i').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
    }


    $('.bounce-view').click(function () {
        sortViewHide()
        sortShow = false

        categoryViewHide()
        categoryShow = false
    })

    $('.glyphicon-plus').click(function () {
        var goodsid=$(this).attr('goodsid')
        data={
            'goodsid':goodsid,

        }
        console.log('+')
        var $that = $(this)
        $.get('/axf/addcart/',data,function (response) {
            if(response.status==0){
                window.open('/axf/login/',target='_self')
            }
            else if (response.status==1){
              $that.prev().html(response.number)
                $that.prev().show()
                $that.prev().prev().show()
            }
        });

    })
    $('.glyphicon-minus').click(function () {
        console.log("-")
        goodsid=$(this).attr('goodsid')
        $that=$(this)
        data={
            'goodsid':goodsid
        }
        $.get('/axf/sucart/',data,function (response) {
            if(response.status==1) {
                if (response.number >0) {
                    $that.next().html(response.number)
                } else {
                    $that.next().hide()
                    $that.hide()
                }
            }
        })
    })
})