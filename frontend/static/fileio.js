
class UploadTask{
    constructor(folder, file, use_aes=false) {
        this.folder = folder;
        this.file = file;
        this.use_aes = use_aes;

        this.task_id = null;
        this.max_chunk_size = null;
        this.detial = null;
    }

    postMeta() {
        $.ajax({
            url: "/api/io/upload/start",
            data: JSON.stringify({
                "name": this.file.name,
                "size": this.file.size,
                "folder": this.folder,
                "aes": this.use_aes,
            }),
            type: 'post',
            async: false,
            contentType: 'application/json',
            dataType: 'JSON',
            success: data => {
                console.log(data);
                if (data.code == 200) {
                    this.task_id = data.detial.id;
                    this.max_chunk_size = data.max_chunk_size;
                    this.detial = data.detial;

                    if (this.use_aes) {
                        self.__aesShakeHand();
                    }
                }
            }
        })
    }

    async doFileUpload() {
        var chunk_id = 0;
        var begin = 0;
        while (begin < this.file.size) {
            var blob = this.file.slice(begin, begin + this.max_chunk_size, {type: "application/octet-stream"});
            var subtask = this.__doChunkUpload(chunk_id, blob);
            this.detial.chunk_status[chunk_id] = subtask;
            chunk_id += 1;
            begin += blob.size;
        }

        await Promise.all(this.detial.chunk_status);
        console.log("Done all.")
    }

    async __doChunkUpload(chunkid, data) {
        if (this.use_aes) {
            data = this.__doAESEnCrypto(chunkid, data);
        }
        var fd = new FormData();
        fd.append('task_id', this.detial.id)
        fd.append('meta', JSON.stringify({
            id: chunkid,
            size: data.size,
            // md5: md5(data),
        }));
        fd.append('chunk_data', data);

        $.ajax({
            url: '/api/io/upload/chunk',
            data: fd,
            type: 'post',
            async: false,
            processData: false,
            contentType: false,
            success: data =>  {
                console.log(data);
                console.log("Done: ", chunkid);
            }
        })
    }

    // Tell Backend the chunks are all done.
    // Do merges and total md5
    postFinish() {
        $.ajax({
            url: "/api/io/upload/finish",
            data: {
                "task_id": this.detial.id,
                // "md5": this.file.size,
            },
            type: 'get',
            async: false,
            success: data => {
                console.log(data);
            }
        })
    }
    
    __aesShakeHand() {
        
    }

    __doAESEnCrypto(chunkid, data) {
        return data;
    }
}

console.log("Load ok.")