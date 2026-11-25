# 1-Ubuntu开发环境与SSH文件共享

[总目录](总目录.md) · [下一篇：CMake](2-CMake.md)

[TOC]

<a id="part-1"></a>

![image-20251020141655670](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20251020141655670.png)

## 1.1 安装和配置ubuntu20

### 1.1.1 安装ubuntu虚拟机

### 1.1.2 ubuntu设置

1. 启用root

   接下来需要设置root用户，在一些情况下，需要用到root权限，打开ubuntu的终端输入

   > sudo passwd

   然后输入ubuntu的密码，接着输入两次unix密码

   Unix密码就是root用户的登录密码，输入以下命令来检查有没有启用root用户

   > su root

   然后输入刚刚设置的Unix密码，可以看到用户名变成root，如下图所示，说明已经启用root成功了。

2. 设置下载源

   ![image-20240630181025625](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630181025625.png)

   ![image-20240630181050576](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630181050576.png)

   > **apt-get update：更新软件源列表（执行这个）**
   >
   > apt-get upgrade：更新已安装的所有的软件

3. 安装VMware Tools

4. 安装vim

   > apt-get install vim

5. 安装net-tools

   > apt install net-tools

<a id="part-2"></a>

## 1.2 Samba 安装与配置

Samba最大的功能就是可以用于Linux与windows系统共享文件夹，搭建SMB服务首先要保证windows和ubuntu网络互通，然后在ubuntu下载安装：

> sudo apt-get install samba

确保 Samba 使用的 Linux 用户对共享目录有相应读写权限；不需要把所有文件统一改为 777。

修改配置：

> sudo vim /etc/samba/smb.conf

添加内容如下:

```
[samba]
comment = smbshare home directory
path = /home/richard/
public = yes
writeable = yes
valid users = richard
create mask = 0664
directory mask = 0777
force user = richard
force group = richard
available = yes
unix charset = UTF-8
dos charset = cp936
```

改完配置文件后保存，然后使用命令设置用户密码

> smbpasswd -a 用户名
>
> sudo smbpasswd -a richard

命令重启 samba 服务:

> sudo service smbd restart

在 windows 上输入“win+r”弹出运行窗口，然后输入 ubuntu 的 IP访问:\\\\ip


## 1.3 samba的使用

> 查看所有的连接
>
> net use 
>
> 删除映射到d盘的连接
>
> net use d: /delete

<a id="part-3"></a>

## 1.4 SSH 远程登录

SSH 用于加密的远程终端访问。发起连接的电脑是客户端，Ubuntu 虚拟机或 RK 开发板是服务端；下面以客户端 Linux/macOS、服务端 Ubuntu/OpenSSH 为例。RK 精简系统可能使用 Dropbear，启动服务及配置文件需要按镜像调整，不能直接套用 Ubuntu 的 systemctl 命令。

### 1.4.1 安装与第一次连接

在 Ubuntu 服务端执行：

```shell
sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh
systemctl status ssh --no-pager
ip -br addr
```

在客户端执行，richard 和 192.168.1.100 都要替换成真实账号与地址：

```shell
ssh richard@192.168.1.100
# SSH 服务若使用 2222 端口：
ssh -p 2222 richard@192.168.1.100
```

首次连接会询问主机指纹，核对目标机器后接受。账号密码属于服务端账号，不是客户端电脑的密码。先用已有普通账号连接，需要管理权限时再使用 sudo。原课堂步骤把 `PermitRootLogin prohibit-password` 改为 `yes`，那是开放 root 密码登录的配置，不是启用 SSH 或密钥登录的必要条件；`prohibit-password` 本身仍允许符合条件的 root 公钥认证。[sshd 配置手册](https://man.openbsd.org/sshd_config)

### 1.4.2 密钥免密码登录的原理

客户端保存私钥，服务端保存对应公钥。登录时客户端用私钥证明身份，服务端验证，因此不必反复输入远程账号密码。

| 文件 | 放在哪一端 | 用途 |
| --- | --- | --- |
| `~/.ssh/id_ed25519_rk` | 客户端 | 私钥，不复制到开发板。 |
| `~/.ssh/id_ed25519_rk.pub` | 客户端生成，公钥内容安装到服务端 | 公钥，可分发给需要登录的目标账号。 |
| `~/.ssh/authorized_keys` | 服务端目标账号的家目录 | 允许该账号登录的公钥列表，一把公钥占一行。 |
| `~/.ssh/known_hosts` | 客户端 | 记录服务端主机身份，与用户公钥列表用途不同。 |

这里的“免密码”指不输入远程账号密码。私钥仍可设置保护口令，并由 ssh-agent 在会话中代管，避免每次重输。[密钥文件说明](https://man.openbsd.org/ssh-keygen)、[公钥认证与文件权限](https://man.openbsd.org/sshd)

### 1.4.3 第一步：在客户端生成密钥

```shell
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "rk-linux-development" -f ~/.ssh/id_ed25519_rk
```

按提示设置私钥保护口令。若已经存在同名密钥，不要覆盖，直接复用已有密钥或另取文件名。生成后会得到私钥与 `.pub` 公钥两个文件。`-t` 指定类型，`-C` 是便于识别的备注，`-f` 指定文件名。[ssh-keygen 手册](https://man.openbsd.org/ssh-keygen)

### 1.4.4 第二步：把公钥安装到服务端

客户端有 ssh-copy-id 时执行：

```shell
ssh-copy-id -i ~/.ssh/id_ed25519_rk.pub richard@192.168.1.100
# 非默认 SSH 端口：
ssh-copy-id -i ~/.ssh/id_ed25519_rk.pub -p 2222 richard@192.168.1.100
```

两条选一条，按真实端口执行。第一次安装公钥通常仍需输入服务端账号密码，或已经拥有另一种可用登录方式。ssh-copy-id 负责把公钥加入远端账号允许列表。[ssh-copy-id 手册](https://manpages.ubuntu.com/manpages/jammy/en/man1/ssh-copy-id.1.html)

客户端没有 ssh-copy-id 时，可在 Linux/macOS 终端用下面的替代方法：

```shell
cat ~/.ssh/id_ed25519_rk.pub | ssh richard@192.168.1.100 \
  'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'
```

此命令传输的是 `.pub` 公钥，采用追加写入，不覆盖已有的其他公钥。确认目标账号正确；安装到 richard 的 authorized_keys 后，应以 richard 登录，而不是换成 root。不要对同一公钥反复手动追加。[authorized_keys 格式](https://man.openbsd.org/sshd)

### 1.4.5 第三步：用指定私钥验证

```shell
ssh -i ~/.ssh/id_ed25519_rk -o IdentitiesOnly=yes richard@192.168.1.100
```

如果提示 `Enter passphrase for key`，是在解锁客户端私钥；如果提示 `richard@… password`，才是回退到远程账号密码。两者含义不同。

使用带保护口令的私钥时，可把它加入当前客户端的 ssh-agent：

```shell
# 若当前终端还没有可用 agent，再启动一个：
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_rk
ssh-add -l
```

ssh-add 时解锁一次，后续连接由 agent 使用该密钥。agent 的存活时间取决于终端、桌面会话或系统集成，重启后可能需要重新加入。[ssh-add 手册](https://man.openbsd.org/ssh-add)

### 1.4.6 第四步：设置连接别名

在客户端 `~/.ssh/config` 中新增一个独立配置块，保留文件里已有的其他主机配置：

```sshconfig
Host rk-board
    HostName 192.168.1.100
    User richard
    Port 22
    IdentityFile ~/.ssh/id_ed25519_rk
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

```shell
chmod 600 ~/.ssh/config
ssh rk-board
scp ./woniu.ko rk-board:/tmp/
```

Host 是自己取的连接别名，HostName 才是真实地址。IdentityFile 选择私钥，IdentitiesOnly 限制尝试的身份；ServerAlive 参数帮助发现失联连接，不会自动修复网络。可以用 `ssh -G rk-board` 查看合并后的有效客户端配置。[ssh_config 手册](https://man.openbsd.org/ssh_config)

### 1.4.7 登录失败时按顺序排查

| 现象 | 检查方向 |
| --- | --- |
| Connection timed out | 地址、网络连通性、路由和防火墙，先确认服务端可达。 |
| Connection refused | 目标地址能响应，但该端口没有服务监听，或被主动拒绝。 |
| Permission denied (publickey) | 用户名、公钥是否装到该账号、指定私钥是否匹配、服务端认证配置。 |
| Too many authentication failures | agent 中身份较多；指定 IdentityFile 并启用 IdentitiesOnly。 |
| 仍要求远程账号密码 | 查看客户端调试日志，确认是否提供并被接受了正确公钥。 |
| Host key verification failed | 核对是否重刷系统、更换机器或连接了错误地址；确认新指纹后才更新 known_hosts。 |

客户端诊断：

```shell
ssh -vvv -i ~/.ssh/id_ed25519_rk -o IdentitiesOnly=yes richard@192.168.1.100
```

Ubuntu 服务端诊断：

```shell
ls -ld ~/.ssh
ls -l ~/.ssh/authorized_keys
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T | grep -E 'pubkeyauthentication|authorizedkeysfile|permitrootlogin'
sudo journalctl -u ssh -n 50 --no-pager
```

确认 `.ssh` 和 authorized_keys 的所有者就是登录账号，通常分别设为 700、600，家目录也不能允许其他用户任意写入。若有 Include 或 Match 块，实际生效配置还可能受连接条件影响；不要只看主配置中的某一行。修改服务端配置后先 `sshd -t` 检查语法，再在 Ubuntu 上执行 `sudo systemctl reload ssh`，保留当前会话并用新终端验证。[sshd](https://man.openbsd.org/sshd)、[sshd_config](https://man.openbsd.org/sshd_config)

### 1.4.8 练习验收

完成一次 `ssh rk-board` 登录、一次 scp 传文件，再开一个新终端确认连接行为。能够解释客户端私钥、远端 authorized_keys、客户端 known_hosts 三者的区别，就算掌握了这部分。

---

[总目录](总目录.md) · [下一篇：CMake](2-CMake.md)
