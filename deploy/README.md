
# 部署手册

> Test Success on Centos 7 

## 0. Prepare 

+ 请先安装 Docker-ce 和 docker-compose
+ 请先 Clone 或 下载本仓库

## 1. 快速部署 HDFS 

使用 install_hdfs.sh 脚本，部署伪分布式Hadoop-hdfs。

```
chmod +x ./install_hdfs.sh
sudo ./install_hdfs.sh
```

脚本包含功能：
+ 检测/安装 JAVA，设置 JAVA_HOME
+ 检测 IP 并设置 Host
+ 生成 ssh-rsakey 并配置免密登录
+ 下载最新的稳定版 hadoop-2
+ 配置
+ 格式化NameNode
+ 启动集群


启动Hdfs: `./hadoop-?/sbin/start-dfs.sh`  
关闭Hdfs: `./hadoop-?/sbin/stop-hdfs.sh`

使用 Jps 查看节点运行状态:
```shell
[root@centos ~]# jps
1606 NameNode
1702 DataNode
1833 SecondaryNameNode
2058 Jps
```

----

## 2. 部署后端与数据库

修改 ./deploy/docker-compose.yml 与 ./backend/config.py 中的数据库密码

打开终端  
cd 到 deploy 文件夹  
运行 docker-compose up -d

## 3. Enjoy at http://ip:80
