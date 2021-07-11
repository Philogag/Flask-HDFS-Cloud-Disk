#!/bin/bash

url="/apache/hbase/stable/"

mirrors[1]="https://mirrors.ustc.edu.cn"

fast_mirror=${mirrors[1]}$url

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
    super_echo "Welcome to the HBase-install-script.
This script will install the Latest Stable HBase-2.*.*"
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
        echo "Install java-1.8.0-openjdk-devel"
        yum install -y java-1.8.0-openjdk-devel
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

##################################### 

function downloadPackage(){
    split_line
    super_echo "-- \e[1;32mDownload Package\e[0m --"

    package_file=`ls . | grep hbase | grep tar.gz$`
    if [ "$package_file" = "" ]; then
        get_version=`curl -sS $urlbase | grep bin.tar.gz | grep -Eo 'hbase-[0-9]+(:?\.[0-9]+)*' | head -n 1`
        echo Download $get_version from $urlbase
        wget ${urlbase}${get_version}-bin.tar.gz  
        package_file=`ls . | grep hbase | grep tar.gz$`
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
        echo -e "\e[1;31m$package_file is broken.\e[0m"
        echo -e "\e[1;31mTry download again.\e[0m"
        rm $package_file -f
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
    __insert "./.bashrc" "export HBASE_HOME=.*" "export HBASE_HOME=$PWD/$floder" 
    __insert "./.bashrc" "export PATH=\$PATH:\$HBASE_HOME.*" "export PATH=\$PATH:\$HBASE_HOME/bin"
    
    __insert "$floder/conf/hbase-env.sh" ".*export JAVA_HOME=.*" "export JAVA_HOME=${JAVA_HOME}"
    __insert "$floder/conf/hbase-env.sh" ".*export HBASE_MANAGES_ZK=.*" "export HBASE_MANAGES_ZK=true"

    source ~/.bashrc
    
    echo -e "\e[1;32mDone.\e[0m"
    return 0
}

function setHbaseSite(){
    split_line
    super_echo "-- \e[1;32mConfiguration hbase-site.yml\e[0m --"

    conf_path=$floder/conf/hbase-site.xml
    
    line=`nl -ba $conf_path | sed -n "/<\/configuration>$/p" | awk '{print $1}'`

    sed -i "$line,\$d" $conf_path

    echo "
    <property><!--指定hbase存储位置-->
        <name>hbase.rootdir</name>
        <value>hdfs://master:9000/hbase</value>
    </property>
    <property><!--指定hbase是分布式的-->
        <name>hbase.cluster.distributed</name>
        <value>true</value>
    </property>
        <property>
        <name>hbase.master</name>
        <value>master:60000</value>
    </property>
    <property>
        <name>hbase.zookeeper.quorum</name>
        <value>master:2181</value>
    </property>
        <property>
        <name>hbase.zookeeper.property.dataDir</name>
        <value>./zoodata</value>
    </property>
 </configuration>" >> $conf_path
    rm $floder/lib/client-facing-thirdparty/slf4j-log4j12-1.7.30.jar
 
    echo -e "\e[1;32mDone.\e[0m"
}

function startDaemon(){
    split_line
    super_echo "-- \e[1;32mStart Hadoop Daemons\e[0m --"

    $floder/bin/start-hbase.sh
    echo ""
    # jps | grep -E 'NameNode|DataNode'
}

function main(){
    Welcome
    checkJava
    setHost
    while true then
    do 
        downloadPackage
        releasePackage
        if [ $? == '0' ]; then
            break
        fi
    done 

    setBashEnv
    setHbaseSite
    # getHadoopConf

    startDaemon

    return 0
}
main

