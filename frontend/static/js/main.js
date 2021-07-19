
$(document).ready(() => {
    load_user_info();
    get_file_list();

    $(document).bind("contextmenu",function(e){
        return false;  // 禁用原生右键菜单
    });
})

function load_user_info() {
    $.ajax({
        url: "/api/auth/user_info",
        type: 'get',
        success: data => {
            if (data.code === 200) {
                a = $("#username")
                a.html(data.user.username);
                notice.info("欢迎回来，" + data.user.username);
            }
            else {
                console.log(data);
            }
        }
    });
}

function get_file_list() {
    $.ajax({
        url: "/api/fs/list",
        type: 'get',
        success: data => {
            console.log(data)
            if (data.code === 200) {
                update_list_table(data);
            }
            else {
                console.log(data);
            }
        }
    });
}

// 文件行单击事件
layui.table.on('row(list_table)', obj => {
    if (obj.data.type == 'folder') { // 仅处理文件夹
        cd_folder(obj.data.id);
    }
});
// 面包屑单击事件
$("#breadcrumb").on('click', '.folder_clickable', e => {
    var folder_id = $(e.target).data('id');
    cd_folder(folder_id);
})


function cd_folder(folder_id) {
    $.ajax({
        url: "/api/fs/cd?id=" + folder_id,
        type: 'get',
        success: data => {
            // console.log(data);
            if (data.code === 200) {
                update_list_table(data);
            }
            else {
                console.log(data);
            }
        }
    });
}

function update_list_table(data) {
    // 加载面包屑
    var bc = $("#breadcrumb")
    bc.data("current", data.detial.id)
    bc.html("")
    var i = 0;
    for (var f of data.detial.root) {
        if (i == 0)
            f.name = "根目录"
        i += 1;
        bc.append('<i class="icofont-rounded-right"></i>')
        bc.append(`<a class="folder_clickable" data-id="${f.id}">${f.name}</a>`)
    }

    // 加载表格
    var itmes = []
    for (var f of data.detial.sons.files) {
        itmes.push({
            type: 'file',
            id: f.id,
            icon: get_icon(f.name),
            name: f.name,
            size: size_pretter(f.size),
            time: f.upload_time
        }) 
    }
    for (var f of data.detial.sons.folders) {
        itmes.push({
            type: 'folder',
            id: f.id,
            icon: '<i class="icofont-ui-folder"></i>',
            name: f.name,
            size: '-',
            time: f.update_time
        }) 
    }
    layui.table.reload('list_table', {
        limit: itmes.length,
        height: 'full-160',
        data: itmes,
        text: {
            none: '文件夹是空的。'
        },
    }, true);
}

function size_pretter(size) {
    size = size * 1.0;
    if (size > 1024 * 1024 * 1024) {
        return "" + (size / 1024 / 1024 / 1024).toFixed(2) + "GB";
    } else if (size > 1024 * 1024) {
        return "" + (size / 1024 / 1024).toFixed(2) + "MB";
    } else if (size > 1024) {
        return "" + (size / 1024).toFixed(2) + "KB";
    } else {
        return "" + size.toFixed(2) + "BB";
    }
}


let icon_map = {
    // exe
    'exe': 'exe',
    // pdf
    'pdf': 'pdf',
    // image
    'png': 'image',
    'jpg': 'image',
    'gif': 'image',
    'svg': 'image',
    'bmp': 'image',
    // zips
    'zip': 'zip',
    'rar': 'zip',
    '7z':  'zip',
    'gz':  'zip',
    'tar': 'zip',
    // music
    'mp3':  'mp3',
    'wav':  'mp3',
    'flac': 'mp3',
}
function get_icon(filename) {
    var ext = filename.split('.').pop();
    var icon = icon_map[ext];
    if (icon == null)
        icon = 'text'
    return `<i class="icofont-file-${icon}"></i>`
}


///////////////////////// Upload Functions /////////////////////////





$("#upload_picker").on("change", e => {
    var file = e.target.files[0];
    var current_folder = $("#breadcrumb").data('current');
    file.folder_id = current_folder;
    uploader.addFiles(file);
})

function show_upload_list() {
    // $("#upload_task_view_container").html('')
    // for (var i = 0; i < 10; i ++){
    //     $("#upload_task_view_container").append($("#upload-task-temp").clone())
    // }
    layer.open({
        title: "上传列表",
        type: 1,
        content: $("#upload_task_view"),
        area: ['50vw', '80vh'],
        closeBtn: false,
        shadeClose: true,
        scrollbar :false,
    });

}

function show_new_upload(task_id, file) {
    var detial_view = $("#upload-task-temp").clone();
    detial_view.data("task_id", task_id);
    detial_view.data("file_id", file.id);
    detial_view.find(".layui-card-header").html(file.name);
    detial_view.attr('id', "task_" + task_id)
    detial_view.find(".layui-progress").attr('lay-filter', "task_" + task_id)
    $("#upload_task_view_container").append(detial_view);
    show_upload_list();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 
// $("#picker").on("change", (e) => {
//     var files = $(e.target).prop('files')[0];
//     // console.log(files);
//     files.folder_id = $("#upload_folder_id").val();
//     uploader.addFiles(files);
// })

let uploader = WebUploader.create({
    swf: 'https://cdn.bootcss.com/webuploader/0.1.1/Uploader.swf',
    auto: true,
    chunked: true,
    chunkSize: 4 * 1024 * 1024,
    chunkRetry: 0,
    threads: 1,
    server: '/api/io/upload/chunk',
});

uploader.on('uploadStart', (file) => {
    // console.log(file);
    // 文件分块传输前自动申请 task_id
    // 并准备 加密 等
    file.md5 = uploader.md5File(file)
    $.ajax({
        url: "/api/io/upload/start",
        data: JSON.stringify({
            "name": file.name,
            "size": file.size,
            "folder": file.source.source.folder_id,
            "aes": false,
        }),
        type: 'post',
        async: false,
        contentType: 'application/json',
        dataType: 'JSON',
        success: data => {
            // console.log(data);
            if (data.code == 200) {
                file.task = data.detial;
                show_new_upload(file.task.id, file);
                notice.info(file.name + "<br>开始上传");
            }
        }
    })
})

uploader.on('uploadBeforeSend', (object, data, headers) => {
    data.task_id = object.file.task.id;
    // console.log(object, data);
})

// 更新任务进度条
uploader.on('uploadProgress', (file , percentage) => {
    task_id = file.task.id;
    layui.element.progress('task_' + task_id, percentage * 100 + '%');
})

uploader.on('uploadSuccess', async (file, response) => {
    // 触发合并
    var Done = false;
    console.log("Check merging.")
    notice.info(file.name + "<br>上传完成，正在校验");
    
    $("#task_" + task_id).find(".layui-progress-bar").addClass("layui-bg-orange")
    layui.element.progress('task_' + task_id, '0%');

    md5 = await file.md5
    while (!Done) {
        await sleep(500)
        $.ajax({
            url: "/api/io/upload/merge",
            data: {
                "task_id": file.task.id,
                "md5": md5
            },
            type: 'get',
            async: false,
            success: data => {
                if (data.status.done && data.status.success) {
                    console.log("File Upload Done.")
                    console.log(data.file);
                    $("#task_" + task_id).find(".layui-bg-orange").removeClass("layui-bg-orange")
                    notice.info(file.name + "<br>校验完成。");
                    get_file_list();
                    setTimeout(() => {
                        $("#upload_task_view_container").remove("#task_" + task_id)
                    }, 5 * 1000);
                }
                if (data.status.done) {
                    Done = true;
                }
                // 此处可以更新合并进度
                // console.log("Merge finish: " + data.status.merged + '/' + data.status.total)
                layui.element.progress('task_' + task_id, 100.0 * data.status.merged / data.status.total + '%');
            }
        })
    }
})

///////////////////////// Drop Folder /////////////////////////

// 阻止浏览器打开新标签，ondrop/ondragover/ondragenter(最好加上这个防兼容问题)
window.ondragover = (e) => e.preventDefault()
window.ondrop = (e) => e.preventDefault()
window.ondragenter = (e) => e.preventDefault()

$("body").on("drop", function (e) {
    console.log(e)
    console.log(e.originalEvent.dataTransfer)
    var fileList = e.originalEvent.dataTransfer.files; //获取文件对象    
    if(fileList.length == 0){                
        return false;            
    }
});

///////////////////////// New Folder /////////////////////////

$("#btn_new_folder").on("click", () => { show_new_folder_view(); })

function show_new_folder_view(task_id, file) {
    $("#name_input_input").val('');
    layer.open({
        title: "新建文件夹",
        type: 1,
        content: $("#name_input_view"),
        area: '300px',
        btn: ['Ok', 'Cancel'],
        closeBtn: false,
        shadeClose: true,
        scrollbar: false,
        
        yes: function (index, layero) { // OK
            var name = $("#name_input_input").val();
            if (name.length <= 0) {
                layer.msg('不能为空', {time: 2000});
                return false;
            }
            $.ajax({
                url: "/api/fs/mkdir?name=" + name,
                type: 'get',
                success: data => {
                    if (data.code === 200) {
                        get_file_list();
                        layer.msg("Ok", {time: 1000});
                        notice.info("新建文件夹：" + name);
                        layer.close(index);
                    }
                },
                error: (req, status, err) => {
                    layer.msg(req.responseJSON.msg, {time: 2000});
                }
            });
        },
        btn2: () => { } // Cancle
    });
}

///////////////////////// Right Menu /////////////////////////


$("div").mousedown(function (e) {
    // console.log(e);
    return checkEvent(e);
})

function checkEvent(e) {
    if (e.which == 3) {
        var tr = $(e.target).parents('tr');
        if (tr.length > 0) {
            menuDisplayAt([e.pageY + 'px', e.pageX + 'px'], tr[0])
        }
        return false;
    }
    return true;
}

function menuDisplayAt(offset, item) {
    var index = $(item).data('index');
    var data = layui.table.getData('list_table');
    
    $("#rightmenu-view").data('index', index);
    $("#rightmenu-view").data('type', data[index].type);
    layer.closeAll();
    layer.open({
        type: 1,
        title: false,
        content: $("#rightmenu-view"),
        offset: offset,
        area: '80px',
        closeBtn: false,
        shade: 0.00001,
        shadeClose: true,
        scrollbar: false,
        resize: false,
        move: false,
    })
}

function menu_get_current() {
    var data = layui.table.getData('list_table');
    return data[$("#rightmenu-view").data('index')]
}

$("#rightmenu-btn-rename").on('click', () => {
    var item = menu_get_current();
    layer.closeAll();
    $("#name_input_input").val(item.name)
    layer.open({
        title: "重命名",
        type: 1,
        content: $("#name_input_view"),
        area: '300px',
        btn: ['Ok', 'Cancel'],
        closeBtn: false,
        shadeClose: true,
        scrollbar: false,
        
        yes: (index, layero) => { // OK
            var name = $("#name_input_input").val();
            if (name.length <= 0) {
                layer.msg('不能为空', {time: 2000});
                return false;
            }
            $.ajax({
                url: "/api/fs/rename?name=" + name + "&id=" + item.id + "&type=" + item.type,
                type: 'get',
                success: data => {
                    if (data.code === 200) {
                        // layer.msg("Ok", {time: 1000});
                        notice.info("重命名：" + item.name + '&nbsp>&nbsp' + name);
                        layer.close(index);
                        get_file_list();
                    }
                },
                error: (req, status, err) => {
                    layer.msg(req.responseJSON.msg, {time: 2000});
                }
            });
        },
        btn2: () => { } // Cancle
    });
})

$("#rightmenu-btn-delete").on('click', () => {
    var item = menu_get_current();
    layer.closeAll();
    layer.open({
        title: "你确定要删除以下文件吗",
        type: 0,
        content: item.name,
        area: '300px',
        btn: ['Ok', 'Cancel'],
        closeBtn: false,
        shadeClose: true,
        scrollbar: false,
        
        yes: (index, layero) => { // OK
            $.ajax({
                url: "/api/fs/delete?id=" + item.id + "&type=" + item.type,
                type: 'get',
                success: data => {
                    if (data.code === 200) {
                        // layer.msg("Ok", {time: 1000});
                        notice.info("删除文件：" + item.name);
                        layer.close(index);
                        get_file_list();
                    }
                },
                error: (req, status, err) => {
                    layer.msg(req.responseJSON.msg, {time: 2000});
                }
            });
        },
        btn2: () => { } // Cancle
    });
})

$("#rightmenu-btn-download").on('click', () => {
    var item = menu_get_current();
    layer.closeAll();
    if (item.type === 'file') {
        $("#download-link").attr('href', '/api/io/download?file=' + item.id);
        $("#download-link span").trigger('click');
        notice.info("即将开始下载：<br>" + item.name)
    } else {
        layer.msg("不支持下载文件夹。")
    }
})