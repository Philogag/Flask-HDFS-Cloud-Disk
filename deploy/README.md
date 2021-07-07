
# 部署手册

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

## 2. 快速部署 HBase

使用 install_hbase.sh 脚本，基于Hadoop部署伪分布式Hbase。

```
chmod +x ./install_hbase.sh
sudo ./install_hbase.sh
```

脚本包含功能：
+ 检测/安装 JAVA，设置 JAVA_HOME
+ 下载最新的稳定版 hbase
+ 配置
+ 启动集群

## 3. 部署后端与数据库