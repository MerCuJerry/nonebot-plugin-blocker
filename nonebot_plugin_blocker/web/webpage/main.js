$(document).ready(function(){
    $.get("query_reply_list",function(result){
        if(result.result=="success"){
            $.each(result.data, function(i, uid){
                $("nav").append($("<li></li>").addClass("botid").text(String(uid)))
            });
            $(".botid").click(function(){
                $(".active").removeClass("active");
                $(this).addClass("active")
                $.get("query_reply",{uin:$(this).text()},function(result){
                    if(result.result=="success"){
                        $.each(result.data, function(key, val){
                            if(typeof(val)=="object"){
                                $.each(val, function(val_key,val_val){
                                    $("[name="+key+"]").find("[name="+val_key+"]").val(val_val)
                                });
                            }
                            $("[name="+key+"]").val(String(val))
                        });
                    }
                });
            });
        }
    });
    $(".submit").click(function(){
        var data = {}
        var reply_on = {}
        var reply_off = {}
        $(".command").serializeArray().map(function(val,key){
            data[val.name] = val.value;
        });
        $(".reply_on").serializeArray().map(function(val,key){
            reply_on[val.name] = val.value;
        });
        $(".reply_off").serializeArray().map(function(val,key){
            reply_off[val.name] = val.value;
        });
        data["blocker_type"] = $(".blocker_type_select").val()
        data["reply_on"] = reply_on
        data["reply_off"] = reply_off
        if(String($(".active").text()) == ""){
            alert("您还没有选择或添加账号");
        }else{
            $.ajax({
                contentType: "application/json",
                data: JSON.stringify(data),
                url: "submit/"+$(".active").text(),
                type: "POST",
                success: function(result){
                    if(result.result=="success"){
                        alert("修改/增加配置成功")
                        if($(".active").hasClass("newadd")){
                            $(".active").removeClass("newadd").bind("click",function(){
                                $.get("query_reply",{uin:$(this).text()},function(result){
                                    if(result.result=="success"){
                                        if(typeof(val)=="object"){
                                            $.each(val, function(val_key,val_val){
                                                $("[name="+key+"]").find("[name="+val_key+"]").val(val_val)
                                            });
                                        }
                                        $.each(result.data, function(key, val){
                                            $("[name="+key+"]").val(String(val))
                                        });
                                    }
                                });
                            });
                        }
                    }else{
                        alert("修改/增加配置失败")
                    }
                }
            });
        }
    });
    $(".delete").click(function(){
        if($(".active").text() == ""){
            alert("您还没有选择或添加账号");
        }else{
            if(confirm("您确定要删除该配置吗")){
                if($(".active").hasClass("newadd")){
                    alert("删除配置成功")
                    $(".active").remove();
                    $(":text").val("")
                    $(".reply_type_select").val("text")
                    $(".is_whitelist_select").val("black")
                }else{
                    $.get("delete",{uin:$(".active").text()},function(result){
                        if(result.result=="success"){
                            alert("删除配置成功")
                            $(".active").remove();
                            $(":text").val("")
                            $(".reply_type_select").val("text")
                            $(".is_whitelist_select").val("black")
                        }else{
                            alert("删除配置失败")
                        }
                    });
                }
            }
        }
    });
});