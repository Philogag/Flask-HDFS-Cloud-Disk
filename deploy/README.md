
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

---

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

**启动Hbase前需启动hdfs**  
启动 HBase: `./hbase-?/bin/start-hbase.sh`  
关闭 HBase: `./hbase-?/bin/stop-hbase.sh && hbase-daemon.sh stop regionserver RegionServer`

使用 Jps 查看节点运行状态:
```shell
[root@centos ~]# jps
2404 HQuorumPeer      -> For Hbase
2564 HMaster          -> For Hbase
1606 NameNode
1702 DataNode
2743 HRegionServer    -> For Hbase
1833 SecondaryNameNode
3613 Jps
```

----

## 3. 部署后端与数据库