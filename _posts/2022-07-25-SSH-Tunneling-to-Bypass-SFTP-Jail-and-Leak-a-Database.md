---
title: SSH Tunneling to Bypass SFTP Jail and Leak a Database
author: skat
categories: misc
layout: post
---

*This writeup is also readable on my [GitHub repository](https://github.com/shawnduong/zero-to-hero-hacking/blob/master/writeups/closed/2022-imaginaryctf.md) and [personal website](https://shawnd.xyz/blog/2022-07-21/SSH-Tunneling-to-Bypass-SFTP-Jail-and-Leak-a-Database).*

Last weekend, I had the pleasure of participating in ImaginaryCTF 2022 with my team, IrisSec. It was a lot of fun and I think we're going to be returning for the next rendition of ImaginaryCTF. The challenges were mostly well-authored, adequately challenging, and very enjoyable.

This writeup is for one of the challenges I completed during the event dealing with using SSH to bypass restrictions to leak a database.

## misc/sequel\_sequel

*Challenge written by Eth007.*

> I stored my flag in my SQL server, but since I followed best practices, there's no way that you can get it!
>
> `ssh ethan@chal.imaginaryctf.org -p 42022` with password `p4ssw0rd10`

Right off the bat, we're given a protocol, username, host, port, and password -- all the necessary information for a successful SSH (**S**ecure **Sh**ell) connection. However, upon connecting to the host on the designated port and logging in with the given credentials, we encounter a problem:

![](/uploads/2022-07-25/00/img00.png)

> This service allows sftp connections only.

SFTP (**S**SH **F**ile **T**ransfer **P**rotocol) is a secure form of FTP built on top of SSH. FTP is a simple protocol for transferring files and is not made with security in mind; there is no encryption. SSH is a protocol that aims to tackle the security problem by establishing a secure connection between two nodes. Thus, FTP extended with SSH provides a secure way to transfer files over a potentially insecure link.

Because the service allows SFTP connections only, we advance by using an SFTP client to connect using the same information. Here, I use the BSD SFTP client to connect:

![](/uploads/2022-07-25/00/img01.png)

Immediately, it appears that there are 3 readable files: `mysqld.cnf`, `setup.sql`, and `sshd_config`. Additionally, it appears that the directory and all files within it are owned by root and we do not have any privileges to modify or create new or existing files in this directory. We're in what appears to be the "root" directory, and we have no way out yet:

![](/uploads/2022-07-25/00/img02.png)

In case the filenames of `mysqld.conf`, `setup.sql`, and `sshd_config` were not apparent, these files detail the MySQL daemon configuration, the setup and structure of an SQL database, and the configuration of the SSH daemon:

![](/uploads/2022-07-25/00/img03.png)

These are all fairly standard and restrictive configurations. Symbolic links, a common attack vector, are even explicitly disabled. The user we are logged in as is SFTP chroot jailed, so what is `/ftp` on the system appears to be `/` to the user's jail and we can go no higher.

However, these configurations tell us something important: there is a MySQL server bound to 127.0.0.1, the localhost. This MySQL server is not accessible from the outside world and can only be accessed within a local context. The MySQL server contains the secret flag we're after. Bypass the SFTP jail to access the MySQL server within a local context, run a query to read from the protected database, and we'll leak the flag.

The thing about SSH is that it's so much more than just a secure shell. SSH provides a medium for file transfer, proxies, tunnels, and more, including an important networking concept: port forwarding. Port forwarding is typically made possible through NAT (**n**etwork **a**ddress **t**ranslation) and involves mapping an "outer" (typically public-facing) address:port to an "inner" (typically internal-facing) address:port in order to allow outside access to inside applications residing on internal machines within a network.

The idea is that we can forward connections from an arbitrary port on our own device to 127.0.0.1:3306 on chal.imaginaryctf.org through SSH. Thus, while the "secure shell" feature of SSH is restricted and "file transfer" feature is jailed, port forwarding still works and we can appear to access the MySQL database in a local (to its perspective) context:

```
$ ssh -p 42022 -N -L 3306:127.0.0.1:3306 ethan@chal.imaginaryctf.org
```

This command connects to `chal.imaginaryctf.org` on port `42022` using `ethan`'s account. `-N` means that we will not execute remote commands; without it, we'd get our connection terminated and the same "sftp only" message as before. `-L` signifies that we're performing local port forwarding as opposed to remote port forwarding; local port forwarding creates an outgoing tunnel from the local device to the remote device, while remote port forwarding creates an outgoing tunnel from the remote device to the local device.

Once the tunnel has been established, we can connect to the SQL database as if it were localhost and leak the flag:

![](/uploads/2022-07-25/00/img04.png)

Very cool challenge. As someone who specializes network security, it's always great to see real networking concepts, misconfigurations, vulnerabilities, and exploits in the CTF scene. By recognizing an oversight in configured restrictions and utilizing lesser-known features of a well-known protocol, we were able to bypass security restrictions to leak data from a database.

Happy hacking!
