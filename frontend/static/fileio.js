
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
  
class UploadTask{
    constructor(folder, file, use_aes=false) {
        this.folder = folder;
        this.file = file;
        this.use_aes = use_aes;
        this.total_md5 = new SparkMD5();

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

    default_onProgress(precent, speed) {
        var s = "";
        if (speed < 1024 * 1024) {
            speed /= 1024; s = "KB/s"
        } else {
            speed /= 1024 * 1024; s = "MB/s"
        }
        console.log(`${precent}, ${speed}${s}`);
    }
    
    async doFileUpload(onProgress = this.default_onProgress) {
        this.chunkUpload_onProgress = onProgress;
        this.start_time = new Date().getTime();
        this.finish_size = 0;

        var chunk_id = 0;
        var begin = 0;
        while (begin < this.file.size) {
            var blob = this.file.slice(begin, begin + this.max_chunk_size, { type: "application/octet-stream" });
            var chunk_size = blob.size;
            var chunk_md5 = await this.__getChunkMD5(blob);
            if (this.use_aes) {
                blob = this.__doAESEnCrypto(chunk_id, blob);
            }
            var subtask = this.__doChunkUpload(chunk_id, blob, chunk_size, chunk_md5);
            this.detial.chunk_status[chunk_id] = subtask;
            chunk_id += 1;
            begin += blob.size;
        }

        await Promise.all(this.detial.chunk_status);
        console.log("Done all.")
    }

    async __doChunkUpload(chunk_id, data_blob, chunk_size, chunk_md5) {
        var fd = new FormData();
        fd.append('task_id', this.detial.id)
        fd.append('meta', JSON.stringify({
            id: chunk_id,
            size: chunk_size,
            md5: chunk_md5
        }));
        fd.append('chunk_data', data_blob);

        $.ajax({
            url: '/api/io/upload/chunk',
            data: fd,
            type: 'post',
            async: false,
            processData: false,
            contentType: false,
            success: data => {
                console.log(data);
                console.log("Done: ", chunk_id);
                this.finish_size += data_blob.size;
                var now = new Date().getTime();
                if (this.chunkUpload_onProgress != null) {
                    this.chunkUpload_onProgress(
                        this.finish_size / this.file.size,
                        this.finish_size / (now - this.start_time)
                    )
                }
            }
        })
    }

    // Tell Backend the chunks are all done.
    // Do merges and total md5
    async postFinish() {
        var Done = false;
        console.log("Check merging.")
        while (!Done) {
            await sleep(500)
            $.ajax({
                url: "/api/io/upload/finish",
                data: {
                    "task_id": this.detial.id,
                },
                type: 'get',
                async: false,
                success: data => {
                    console.log(data)
                    if (data.status.done && data.status.success) {
                        console.log("File Upload Done.")
                        console.log(data.file);
                    }

                    if (data.status.done) {
                        Done = true;
                    }
                }
            })
        }
    }

    async __asyncReadBytes(blob) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader()
            reader.readAsArrayBuffer(blob)
            reader.onload = e => {
                resolve(e.target.result)
            }
        })
    }

    async __getChunkMD5(chunk_blob) {
        var bytes = await this.__asyncReadBytes(chunk_blob);
        // console.log(typeof (bytes), bytes);
        this.total_md5.appendBinary(bytes);
        var chunk_md5 = SparkMD5.ArrayBuffer.hash(bytes);
        // console.log(chunk_md5);
        return chunk_md5;
    }
    
    __getTotalMD5() {
        return this.total_md5.end()
    }

    __aesShakeHand() {
        
    }

    __doAESEnCrypto(chunkid, data) {
        return data;
    }
}

console.log("Load ok.")