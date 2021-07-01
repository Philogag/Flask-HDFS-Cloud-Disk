# Flask 后端

## 目录

[TOC]

---

##RESTful API

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

| Return Code | Detial             |
| ----------- | ------------------ |
| 200         | success            |
| 403.1       | User not found.    |
| 403.2       | Password is wrong. |

```
{
  "code": 403,
  "msg": "User not found."
}
```

#### GET /auth/check

检查当前登录状态

| Return Code | Detial       |
| ----------- | ------------ |
| 200         | Is logined.  |
| 401         | Not logined. |

```
{
  "code": 401,
  "msg": "401 Unauthorized: The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
}
```

#### GET /auth/logout

登出

| Return Code | Detial                             |
| ----------- | ---------------------------------- |
| 200         | Success.                           |
| 401         | Not login now, do not need logout. |

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

| Return Code | Detial                              |
| ----------- | ----------------------------------- |
| 200         | Success.                            |
| 403.1       | Username has been registered.       |
| 403.2       | Confirm password dose not the same. |

