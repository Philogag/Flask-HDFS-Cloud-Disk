# Flask 后端

## 目录

- [Flask 后端](#flask-后端)
  - [目录](#目录)
  - [RESTful API](#restful-api)
      - [GET /hello](#get-hello)
    - [Auth](#auth)
      - [状态码概览](#状态码概览)
      - [POST /auth/login](#post-authlogin)
      - [GET /auth/check](#get-authcheck)
      - [GET /auth/logout](#get-authlogout)
      - [POST /auth/regist](#post-authregist)
    - [FileSystem](#filesystem)
      - [状态码概览](#状态码概览-1)
      - [GET /fs/list](#get-fslist)
      - [GET /fs/refresh](#get-fsrefresh)
      - [GET /fs/mkdir?name=\<name\>](#get-fsmkdirnamename)
      - [GET /fs/cd?id=\<id\>](#get-fscdidid)
      - [GET /fs/move?](#get-fsmove)
      - [GET /fs/rename?](#get-fsrename)
      - [GET /fs/delete?](#get-fsdelete)
    - [IO (Upload/Download)](#io-uploaddownload)
      - [fileio.js](#fileiojs)
        - [class UploadTask(folder_id: str, file: File, use_ase: Boolean)](#class-uploadtaskfolder_id-str-file-file-use_ase-boolean)
          - [UploadTask.postMeta()](#uploadtaskpostmeta)
          - [UploadTask.doFileUpload()](#uploadtaskdofileupload)
          - [UploadTask.postFinish()](#uploadtaskpostfinish)
      - [POST /api/io/upload/start](#post-apiiouploadstart)
      - [POST /api/io/aes_shakehand （TODO）](#post-apiioaes_shakehand-todo)
      - [POST /api/io/upload/chunk](#post-apiiouploadchunk)
      - [GET /api/io/upload/finish](#get-apiiouploadfinish)

---

## RESTful API

**所有URL均带 `/api` 前置，下方url均省略不写**

> 如 GET /hello 实际为 GET http://hostname/api/hello

所有 api url 均有返回 code 字段，代表响应概览。

除200外，其他状态码均由两部分组成：HTTP状态码.自定义状态码

具体值定义见下。

---

#### GET /hello

后端握手，心跳

| Return Code | Detial  |
| ----------- | ------- |
| 200         | success |

```json
{
  "code": 200,
  "msg": "hello"
}
```

---

### Auth

#### 状态码概览

| Return Code | Detial           |
| ----------- | ---------------- |
| 200         | Success.         |
| 406.00001   | 登录用户不存在。 |
| 406.00002   | 登录密码错误。   |
| 401         | 未登录           |
| 406.00003   | 用户名已被注册   |
| 406.00004   | 注册密码不匹配   |

#### POST /auth/login

登录
```http
POST /auth/login
Content-Type: application/json

{
    "username": "philogag",
    "password": "123456"
}
```

```json
{
  "code": 200,
  "info": {
    "id": "xxxxxxxx",
    "last_login": "Thu, 08 Jul 2021 20:59:05 GMT",
    "regist_time": "Thu, 08 Jul 2021 19:44:44 GMT",
    "username": "philogag"
  },
  "msg": "Login successfully"
}
```

#### GET /auth/check

检查当前登录状态，已登录报 200，未登录报 401

#### GET /auth/logout

登出

若未登录访问此url，报 401

#### POST /auth/regist

注册

```http
POST /auth/regist
Content-Type: application/json

{
  "username": "philogag",
  "password": "123456",
  "password2": "123456"
}
```

```json
{
  "code": 200,
  "info": {
    "id": "xxxxxxx",
    "last_login": "Thu, 08 Jul 2021 20:59:05 GMT",
    "regist_time": "Thu, 08 Jul 2021 19:44:44 GMT",
    "username": "philogag"
  },
  "msg": "Regist successfully."
}
```

---

### FileSystem

通过 cookie 中的 <t id="current_path_id">current_path_id</t>  字段保存 当前所在文件夹

登录时自动检查 **cookie** 中的 **旧id** 是否有权限。若无权限（即用户不匹配），则自动设置为 **用户根目录 `~`**

注册成功后自动设置为 **用户根目录 `~`**

#### 状态码概览

| Return Code | Detial                                           |
| ----------- | ------------------------------------------------ |
| 200         | Success.                                         |
| 403.10000   | 缺少参数。                                        |
| 404.10001   | 当前文件夹不存在。                               |
| 403.10002   | 权限错误，文件夹所有者和当前登录不匹配。         |
| 400.10003   | 新建文件（夹）名字为空                           |
| 400.10004   | 新建文件（夹）名字包含非法字符，默认为/\:*?"<>\| |





#### GET /fs/list

#### GET /fs/refresh

二者等价，获取 <a href="#current_path_id">current_path_id</a> 的详细信息，包括到根的路径，子目录，子文件夹等

```json
{
  "code": "200",
  "detial": {
    "id": "xxxxx",
    "name": "test",
    "root": [
      {
        "id": "xxxxx",
        "name": "~",
        "size": 2,
        "update_time": "Thu, 08 Jul 2021 19:44:44 GMT"
      }
    ],
    "size": 2,
    "sons": {
      "files": [{
        "id": "xxxxx",
        "name": "filename",
        "size": 2,
        "update_time": "Thu, 08 Jul 2021 19:44:44 GMT"
      }],
      "folders": [{
        "id": "xxxxxx",
        "name": "foldername",
        "size": 0,
        "update_time": "Thu, 08 Jul 2021 19:44:44 GMT"
      }]
    },
    "update_time": "Thu, 08 Jul 2021 20:06:10 GMT"
  }
}
```

其中 root 字段为 **当前位置** 到 **根目录** 的路径，第一个为根，按深度顺序排列



#### GET /fs/mkdir?name=\<name\>

在 <a href="#current_path_id">current_path_id</a> 下新建文件夹，

检查非空且不包含非法字符，默认为 `/\:*?"<>\|` 
可通过 BANNED_CHARSET 进行配置

```json
{
  "code": "200",
  "msg": "ok",
  "new_id": "xxxxx"  // 新文件夹id
}
```



#### GET /fs/cd?id=\<id\>

设置 <a href="#current_path_id">current_path_id</a> 为 id 所指文件夹

检测权限，

返回形如 /fs/list

#### GET /fs/move?

移动文件和文件夹到指定目录
| Args        | Detial                                           |
| ----------- | ------------------------------------------------ |
| type        | 目标类型，文件"file"还是文件夹"folder"                 |
| id          | 目标id                       |
| target      | 移动到的指定id的文件夹内                       |


#### GET /fs/rename?

重命名文件或文件夹
| Args        | Detial                                           |
| ----------- | ------------------------------------------------ |
| type        | 目标类型，文件"file"还是文件夹"folder"                 |
| id          | 目标id                       |
| name        | 新名字                       |

#### GET /fs/delete?

| Args | Detial                                 |
| ---- | -------------------------------------- |
| type | 目标类型，文件"file"还是文件夹"folder" |
| id   | 目标id                                 |



---

### IO (Upload/Download)

前端可以直接使用 static/fileio.js

#### fileio.js

这是一个使用 JavaScript 封装的并发文件上传/下载接口实现，可以直接调用

##### class UploadTask(folder_id: str, file: File, use_ase: Boolean)

+ folder_id : 上传目标文件夹
+ file : 上传文件，使用 input 可以选中文件
+ use_ase : 是否使用 AES 加密 （未实现）

###### UploadTask.postMeta()

初始化上任务，预分块，AES密钥验证握手

###### UploadTask.doFileUpload()

基于异步的文件分块上传，文件块大小由后端决定，默认4MB

###### UploadTask.postFinish()

结束上传任务，校验文件总MD5，文件合并，推入hdfs或hbase





#### POST /api/io/upload/start

+ 初始化上传任务
+ 缓存文件元数据（不直接写入File表中）

+ 新建缓存文件夹
+ 准备AES密钥



#### POST /api/io/aes_shakehand （TODO）

+ 前后端 AES 密钥握手校验



#### POST /api/io/upload/chunk

+ 单块文件上传

```http
Content-Type: multiform/form-data

{
	"task_id": task id,
	"meta": {
	    "id": chunk id,
	    "size": raw chunk size; when aes, size may bigger.
	    "md5": md5 of raw chunk
	},
	"chunk_data": Blob( raw/aes data , {type: "application/octet-stream"})
}
```

#### GET /api/io/upload/finish

+ 触发文件块归并
+ 总MD5计算



| Args    | Detial |
| ------- | ------ |
| task_id | 任务ID |