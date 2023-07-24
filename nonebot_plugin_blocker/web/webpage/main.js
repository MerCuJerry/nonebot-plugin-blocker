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
                            $("[name="+key+"]").val(val)
                        });
                    }
                });
            });
        }
    });
    $(".submit").click(function(){
        var data = {}
        $(".blocker_submit_form").serializeArray().map(function(val,key){
            data[val.name] = val.value;
        });
        var newdata = {}
        if(String($(".active").text()) == ""){
            alert("您还没有选择或添加账号");
        }else{
            newdata[String($(".active").text())] = data
            console.log(newdata)
            $.ajax({
                contentType: "application/json",
                data: JSON.stringify(newdata),
                url: "submit",
                type: "POST",
                success: function(result){
                    if(result.result=="success"){
                        alert("修改/增加配置成功")
                        if($(".active").hasClass("newadd")){
                            $(".active").removeClass("newadd").bind("click",function(){
                                $.get("query_reply",{uin:$(this).text()},function(result){
                                    if(result.result=="success"){
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