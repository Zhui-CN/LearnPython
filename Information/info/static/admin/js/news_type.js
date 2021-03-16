function getCookie(name) {
    let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    let $a = $('.edit');
    let $a2 = $('.edit2');
    let $add = $('.addtype');
    let $pop = $('.pop_con');
    let $cancel = $('.cancel');
    let $confirm = $('.confirm');
    let $error = $('.error_tip');
    let $input = $('.input_txt3');
    let sHandler = 'edit';
    let sId = 0;

    $a.click(function () {
        sHandler = 'edit';
        sId = $(this).parent().siblings().eq(0).html();
        $pop.find('h3').html('修改分类');
        $pop.find('.input_txt3').val($(this).parent().prev().html());
        $pop.show();
    });

    $add.click(function () {
        sHandler = 'add';
        $pop.find('h3').html('新增分类');
        $input.val('');
        $pop.show();
    });

    $a2.click(function () {
        sHandler = 'del';
        sId = $(this).parent().siblings().eq(0).html();
        $pop.find('h3').html('删除分类');
        $pop.find('.mt50').html('');
        $pop.show();
    });

    $cancel.click(function () {
        $pop.hide();
        $error.hide();
    });

    $input.click(function () {
        $error.hide();
    });

    $confirm.click(function () {
        let params = {}
        if (sHandler === 'edit') {
            let sVal = $input.val();
            if (sVal === '') {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "action": "edit",
                "id": sId,
                "name": sVal,
            };
        } else if (sHandler === 'add') {
            let sVal = $input.val();
            if (sVal === '') {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "action": "add",
                "name": sVal,
            }
        } else {
            params = {
                "action": "del",
                "id": sId
            }
        }
        // TODO 发起修改分类请求
        $.ajax({
            url: "/admin/add_category",
            method: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            contentType: "application/json",
            success: function (resp) {
                if (resp.errno === "0") {
                    // 刷新当前界面
                    location.reload();
                } else {
                    $error.html(resp.errmsg).show();
                }
            }
        })
    })
})