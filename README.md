# MPI 双向编程接口 (Minecraft Programming Interface)

<div align="center">

![Static Badge](https://img.shields.io/badge/Python-3.x-blue)
![Static Badge](https://img.shields.io/badge/Minecraft-1.20.x-green)
![Static Badge](https://img.shields.io/badge/Java-17-orange)

<image src="https://projects.async.ltd/mpi/mpi_filled_256x.png" width="10%">
</div>

## 简介 Introduction

MPI (Minecraft Programming Interface) 是面向Python的Minecraft**双向编程接口**。

> ### 什么是双向编程接口？
>
> 双向编程接口指连接接口的两者可以主动调用对方。
> 例如RCON只能由外部程序向Minecraft服务器发送命令，而Minecraft服务器无法主动调用外部程序。因此，RCON不是双向编程接口。

MPI 不仅支持单个脚本进行Minecraft编程，也支持导入**程序包**。

## 安装 Installation

通过url安装Java端插件：([MPI-1.0-SNAPSHOP.jar](https://projects.async.ltd/mpi/MPI-1.0-SNAPSHOT.jar))

```bash
wget -O MPI-1.0-SNAPSHOT.jar https://projects.async.ltd/mpi/MPI-1.0-SNAPSHOT.jar
```

通过bash安装器安装Python端接口：([mpi-installer.bash](https://projects.async.ltd/mpi/mpi-installer.bash))

```bash
wget -O mpi-installer.bash https://projects.async.ltd/mpi/mpi-installer.bash
bash mpi-installer.bash
```

通过url下载压缩包并手动安装Python端接口：([mpi-0.0.4.tar.gz](https://projects.async.ltd/mpi/versions/mpi-0.0.4.tar.gz))

```bash
wget -O mpi-0.0.4.tar.gz https://projects.async.ltd/mpi/versions/mpi-0.0.4.tar.gz
```
