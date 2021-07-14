






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

        this.chunk_fail = 10;
    }

    postMeta() {
        return new Promise((resolve, reject) => {
            if (this.file == null) {
                resolve();
            }
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
                    if (data.code == 200) {
                        this.task_id = data.detial.id;
                        this.max_chunk_size = data.max_chunk_size;
                        this.detial = data.detial;
    
                        if (this.use_aes) {
                            self.__aesShakeHand();
                        }
                        this.uploader = WebUploader.create({
                            formData: {
                                task_id: this.task_id
                            },
                            chunked: true,
                            chunkSize: this.max_chunk_size,
                            chunkRetry: 5,
                            server: '/api/io/upload/chunk',
                        });
                        resolve(true);
                    }
                }
            })
            
        })
    }
    
    doFileUpload() {
        this.uploader.addFiles(this.file);
        this.uploader.upload();
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

    async cancle() {
        this.uploader.cancelFile(this.file);
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

    __aesShakeHand() {
        
    }

    __doAESEnCrypto(chunkid, data) {
        return data;
    }
}

console.log("Load ok.")