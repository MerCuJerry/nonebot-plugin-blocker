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
                            $("[name="+key+"]").val(val)
                        });
                    }
                });
            });
        }
    });
    $(".submit").click(function(){
        var raw_data = {}
        var reply_on = {}
        var reply_off = {}
        $(".command").serializeArray().map(function(val,key){
            raw_data[val.name] = val.value;
        });
        $(".reply_on").serializeArray().map(function(val,key){
            reply_on[val.name] = val.value;
        });
        $(".reply_off").serializeArray().map(function(val,key){
            reply_off[val.name] = val.value;
        });
        raw_data["reply_on"] = reply_on
        raw_data["reply_off"] = reply_off
        var data = {}
        if(String($(".active").text()) == ""){
            alert("您还没有选择或添加账号");
        }else{
            data[String($(".active").text())] = raw_data
            console.log(data)
            $.ajax({
                contentType: "application/json",
                data: JSON.stringify(data),
                url: "submit",
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
                                            $("[name="+key+"]").val(val)
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
    $(".add").click(function(){
        $(".active").removeClass("active");
        if(!$(this).parent().children("span").hasClass("inputbox")){
            $("nav").append($("<span></span>").addClass("inputbox")
            .append($("<input>").attr("type","text")
            .attr("onkeyup","value=value.replace(/[^\\d]/g,'').replace(/^0{1,}/g,'')")
            .addClass("botid_input")));
            $(".botid_input").focus();
            $(".botid_input").bind("keydown blur",function(key){
                if(key.which==13||key.which==0){
                    if($(this).val()==""){
                        alert("请填写需要配置的账号")
                        $(this).blur().end()
                    }else{
                        var mark=false
                        var input_text=$(".botid_input").val()
                        $(".botid").each(function(){
                            if($(this).text()==input_text){
                                mark=true
                            }
                        });
                        if(mark){
                            alert("已经存在相同的账号")
                            $(this).blur().end()
                        }else{
                            $("nav").append($("<li></li>").addClass("botid").addClass("newadd").addClass("active").text(input_text));
                            $(this).parent().remove();
                            $(".newadd").click(function(){
                                $(".active").removeClass("active");
                                $(this).addClass("active");
                            });
                        }
                    }
                }
            });
        }else{
            $(".botid_input").focus();
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
                    $("select").val("text")
                }else{
                    $.get("delete",{uin:$(".active").text()},function(result){
                        if(result.result=="success"){
                            alert("删除配置成功")
                            $(".active").remove();
                            $(":text").val("")
                            $("select").val("text")
                        }else{
                            alert("删除配置失败")
                        }
                    });
                }
            }
        }
    });
});