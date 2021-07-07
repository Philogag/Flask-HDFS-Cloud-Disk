#!/bin/bash

######################################## Super Echo ###########################################
IFS=$'\n'
function echo_center()
{
  WINDWO_WIDE=`stty size|awk '{print $2}'`
  len=${#1}
  w=`expr $WINDWO_WIDE - $len`
  w=`expr $w / 2`
  if [ $w -ge '1' ]; then
    spaces=`yes " " | sed $w'q' | tr -d '\n'`
  else
    spaces=""
  fi
  echo -e "${spaces}${1}"
}

function super_echo()
{
  echo ""
  for i in ${1}
  do 
    echo_center $i
  done
  echo ""
}

function split_line(){
    WINDWO_WIDE=`stty size|awk '{print $2}'`
    line=`yes "-" | sed $WINDWO_WIDE'q' | tr -d '\n'`
    echo $line
}

function getIPV4(){
    eth=`route | tail -n 1 | awk '{print $NF}'`
    ip=`ip addr show dev ens33 | grep inet | grep -v inet6 | awk '{print $2}' | awk -F / '{print $1}'`
    echo Current IP=$ip
}

function __insert(){
    filename=$1
    search=$2
    value=$3

    if [ ! -f $filename ]; then
        touch $filename
    fi
    
    echo Add \"$value\" To $filename
    get=`sed -n "/$search/p" $filename`
    if [ -z "$get" ]; then
        echo $value >> $filename
    else
        sed -i "s|$search|$value|g" $filename
    fi
}

###################################### Main Part ######################################

function Welcome(){
    split_line
    super_echo "Welcome to the hadoop-install-script.
This script will install the Latest Stable hadoop-2.*.*"
    return 0
}

function checkJava(){
    source /etc/bashrc
    source ~/.bashrc
    source /etc/profile
    split_line
    super_echo "-- \e[1;32mCheck Java\e[0m --"
    JAVA_HOME=$JAVA_HOME
    if [ -n "$JAVA_HOME" ]; then
        echo JAVA_HOME=$JAVA_HOME
        return
    else 
        echo JAVA_HOME not found.
    fi
    javabin=`whereis -b javac | sed 's/ /\n/g ' | grep bin`
    if [ -z "$javabin" ]; then
        echo Java not found.
        echo "Install java-1.8.0-openjdk"
        yum install -y java-1.8.0-openjdk
        javabin=`whereis -b java | sed 's/ /\n/g ' | grep bin`
    fi
    echo "Locate JAVA_HOME"
    while [ -L "$javabin" ];
    do 
        javabin=`ls -al "$javabin" | awk '{print $NF}'`
    done
    JAVA_HOME=${javabin::-10}
    echo JAVA_HOME=$JAVA_HOME
    echo -e "\e[1;32mDone.\e[0m"
}

function setHost(){
    split_line
    super_echo "-- \e[1;32mSet Hosts\e[0m --"
    getIPV4
    __insert /etc/hosts ".*master$" "$ip master"
    echo -e "\e[1;32mDone.\e[0m"
}

function setSSH(){
    split_line
    super_echo "-- \e[1;32mConfiguration SSH\e[0m --"
    
    if [ -f "~/.ssh/id_rsa.pub" ]; then
        super_echo "\e[1;33mYou don't have the rsa key yet.
 Create one now.\e[0m"
        ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
    fi
    pubkey=`cat ~/.ssh/id_rsa.pub`
    
    sshhost=${pubkey##*\ }
    __insert ~/.ssh/authorized_keys "$sshhost" "$pubkey" 

    hosts=("0.0.0.0" "localhost" "master,$ip")
    for authhost in ${hosts[@]} # 添加host指纹白名单
    do
        echo Add $authhost to known_hosts
        fp=`ssh-keyscan -t ECDSA $authhost`
        __insert ~/.ssh/known_hosts "$authhost" "$fp"  
    done
    echo -e "\e[1;32mDone.\e[0m"
}

##################################### 

function downloadPackage(){
    split_line
    super_echo "-- \e[1;32mDownload Package\e[0m --"

    package_file=`ls . | grep hadoop | grep tar.gz$`
    if [ "$package_file" = "" ]; then
        get_version=`curl -S http://mirrors.ustc.edu.cn/apache/hadoop/common/stable2/ | grep rat.txt | grep -Eo 'hadoop-[0-9]+(:?\.[0-9]+)*' | head -n 1`
        echo Download $get_version from https://mirrors.tuna.tsinghua.edu.cn
        wget http://mirrors.ustc.edu.cn/apache/hadoop/common/stable2/$get_version.tar.gz
        package_file=`ls . | grep hadoop | grep tar.gz$`
    fi
    echo Package: $package_file
    echo -e "\e[1;32mDone.\e[0m"
}

function releasePackage(){
    split_line
    super_echo "-- \e[1;32mRelease Package\e[0m --"

    floder=${package_file%\.tar.gz}
    if [ -d $floder ]; then
        echo Floder exist, remove and reinstall
        rm -rf $floder
    fi
    mkdir $floder
    echo Release package: $package_file -\> $floder
    tar -zxf $package_file -C $floder
    if [ $? != '0' ]; then
        echo Release Failed!
        return 1
    fi
    echo Release done.
    inname=`ls $floder`
    mv $floder/*/* $floder/
    rm $floder/$inname -rf
    
    echo -e "\e[1;32mDone.\e[0m"
    return 0
}

function setBashEnv(){
    split_line
    super_echo "-- \e[1;32mConfiguration System Variables\e[0m --"
    __insert "./.bashrc" "export HADOOP_HOME=.*" "export HADOOP_HOME=$PWD/$floder" 
    __insert "./.bashrc" "export PATH=\$PATH:\$HADOOP_HOME.*" "export PATH=\$PATH:\$HADOOP_HOME/bin"
    
    __insert "$floder/etc/hadoop/hadoop-env.sh" "export JAVA_HOME=.*" "export JAVA_HOME=${JAVA_HOME}"

    source ~/.bashrc
    
    echo -e "\e[1;32mDone.\e[0m"
    return 0
}

function setCoreSite(){
    split_line
    super_echo "-- \e[1;32mConfiguration core-site.yml\e[0m --"

    conf_path=$floder/etc/hadoop/core-site.xml
    
    line=`nl -ba $conf_path | sed -n "/<configuration>$/p"`
    line=`echo $line | sed "s/[^0-9]//g"`

    echo Delete old config from line $line.
    sed -i "$line,\$d" $conf_path

    echo Write new config.
    echo "<configuration>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>$PWD/$floder/data</value>
    </property>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://master:9000</value>
    </property>
 </configuration>" >> $conf_path
 
    echo -e "\e[1;32mDone.\e[0m"
}

function setHdfsSite(){
    split_line
    super_echo "-- \e[1;32mConfiguration hdfs-site.yml\e[0m --"

    conf_path=$floder/etc/hadoop/hdfs-site.xml
    
    line=`nl -ba $conf_path | sed -n "/<configuration>$/p"`
    line=`echo $line | sed "s/[^0-9]//g"`

    echo Delete old config from line $line.
    sed -i "$line,\$d" $conf_path

    echo Write new config.
    echo "<configuration>
    <property>
        <name>hdfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.http-address</name>        //配置namenode 地址
        <value>master:50070</value>
    </property>
    <property>
        <name>dfs.namenode.secondary.http-address</name>        //配置 secondarynamenode 地址
        <value>master:50090</value>
    </property>
    <property>
        <name>hdfs.namenode.name.dir</name>
        <value>$PWD/$floder/data/dfs/name</value>
    </property>
    <property>
        <name>hdfs.datanode.data.dir</name>
        <value>$PWD/$floder/data/dfs/data</value>
    </property>
 </configuration>" >> $conf_path
 
    echo -e "\e[1;32mDone.\e[0m"
}

function formatNameNode(){
    split_line
    super_echo "-- \e[1;32mFormat NameNode\e[0m --"

    if [ -d "$PWD/$floder/data/dfs/" ]; then
        rm -rf "$PWD/$floder/data/dfs/*"
    fi

    $floder/bin/hdfs namenode -format

    if [ $? -eq '0' ]; then
        super_echo "\e[1;32mFormat NameNode Success!\e[0m"
    else
        super_echo "\e[1;31mFormat NameNode Failed!\e[0m"
        split_line
        exit -1
    fi
}

function startHadoopDaemon(){
    split_line
    super_echo "-- \e[1;32mStart Hadoop Daemons\e[0m --"

    $floder/sbin/start-dfs.sh
    echo ""
    jps | grep -E 'NameNode|DataNode'
}

function main(){
    Welcome
    checkJava
    setHost
    setSSH
    while true then
    do 
        downloadPackage
        releasePackage
        if [ $? == '0' ]; then
            break
        fi
    done 

    setBashEnv
    setCoreSite
    setHdfsSite

    formatNameNode
    startHadoopDaemon

    return 0
}
main

