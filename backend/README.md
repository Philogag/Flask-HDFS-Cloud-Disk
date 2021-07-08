# Flask 后端

## 目录

[TOC]

---

## RESTful API

**所有URL均带 `/api` 前置，下方url均省略不写**

> 如 GET /hello 实际为 GET http://hostname/api/hello

所有 api url 均有返回 code 字段，代表响应概览。

除200外，其他状态码均由两部分组成：HTTP状态码.自定义状态码

具体值定义见下。



#### GET /hello

后端握手，心跳

| Return Code | Detial  |
| ----------- | ------- |
| 200         | success |

```
{
  "code": 200,
  "msg": "hello"
}
```

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
```
POST /auth/login
Content-Type: application/json

{
    "username": "philogag",
    "password": "123456"
}
```

```
{
  "code": 403,
  "msg": "User not found."
}
```

#### GET /auth/check

检查当前登录状态，已登录报 200，未登录报 401

#### GET /auth/logout

登出

若未登录访问此url，报 401

#### POST /auth/regist

注册

```
POST /auth/regist
Content-Type: application/json

{
    "username": "philogag",
    "password": "123456",
    "password-confirm": "123456",
    "data": {
        "desc": "Any other things can put on 'data'."
    }
}
```





---

### FileSystem

通过 cookie 中的 <p id="current_path_id">current_path_id</p>  字段保存 当前所在文件夹

登录时自动检查 **cookie** 中的 **旧id** 是否有权限。若无权限（即用户不匹配），则自动设置为 **用户根目录 `~`**

注册成功后自动设置为 **用户根目录 `~`**

#### 状态码概览

| Return Code | Detial                                           |
| ----------- | ------------------------------------------------ |
| 200         | Success.                                         |
| 403.10001   | 当前文件夹不存在。                               |
| 403.10002   | 权限错误，文件夹所有者和当前登录不匹配。         |
| 400.10003   | 新建文件（夹）名字为空                           |
| 400.10004   | 新建文件（夹）名字包含非法字符，默认为/\:*?"<>\| |





#### GET /fs/list

#### GET /fs/refresh

二者等价，获取 <a href="#current_path_id">current_path_id</a> 的详细信息，包括到根的路径，子目录，子文件夹等

```
{
  "code": "200",
  "detial": {
    "id": "60e6ea32bffd7b9c16bc75a8",
    "name": "test",
    "root": [
      {
        "id": "60e6e52c0a9a80ba7867e331",
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



#### GET /fs/cd?id=\<id\>

设置 <a href="#current_path_id">current_path_id</a> 为 id 所指文件夹

检测权限，

返回形如 /fs/list

