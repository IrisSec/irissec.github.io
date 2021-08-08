---
title: Performing Digital Forensics on an Apple Tablet to Recover Evidence
author: skat
categories: forensics
layout: post
---

*This writeup is also readable on my [GitHub repository](https://github.com/shawnduong/zero-to-hero-hacking/blob/master/writeups/closed/2021-uiuctf.md) and [personal website](https://shawnd.xyz/blog/2021-08-05/Performing-Digital-Forensics-on-an-Apple-Tablet-to-Recover-Evidence).*

Last weekend, I had the pleasure of competing at UIUCTF 2021 hosted by the University of Illinois at Urbana-Champaign. This was my team's second time competing at UIUCTF and we scored 3rd out of 658 teams this year. It was a great experience and I learned a lot while also having a lot of fun hacking with my team! I think we really pulled it together and everyone gave 110% this event, and I'm of course always grateful to be surrounded by such talented individuals that I can learn from.

This writeup is for a pair of challenges that I did called **forensics/Tablet 1** and **forensics/Tablet 2** authored by WhiteHoodHacker of UIUC's SIGPwny. For someone who specializes in network security and digital forensics, I think that this is actually the first time I've ever written a forensics writeup! These challenges involved performing digital forensics on an Apple tablet to recover evidence and investigate an individual.

## Contents

- [forensics/Tablet 1](#forensicstablet-1)
  - [Debriefing](#debriefing-1)
- [forensics/Tablet 2](#forensicstablet-2)
  - [Debriefing](#debriefing-2)
- [Conclusion](#conclusion)

## forensics/Tablet 1

*Challenge written by WhiteHoodHacker.*

> Red has been acting very sus lately... so I took a backup of their tablet to see if they are hiding something!
> 
> It looks like Red has been exfiltrating sensitive data bound for Mira HQ to their own private server. We need to access that server and contain the leak.

<!-- I have to host this on my personal site because GitHub doesn't like how large it is. -->
Files: [`tablet.tar.gz`](https://shawnd.xyz/blog/uploads/2021-08-05/tablet.tar.gz)

Checksum (SHA-1):

```
27dfb3448130b5e4f0f73a51d2a41b32fd81b284  tablet.tar.gz
```

To preface, I just want to say that this was a really fun challenge! It involves performing digital forensics on an Apple tablet using a given filesystem backup, investigating a (fictional) target, interacting with SQLite databases used by some common applications, and using evidence discovered through the forensics process to hack into another server. The ideas and procedures explored are pretty neat and are definitely something that would be encountered in real-life operations!

Let's first start off the challenge by getting oriented. Based off of the challenge description, we have a few key pieces of information:

- Our target is "Red."
- We have a backup of Red's tablet.
- Red exfiltrated data to a private server.
- Our objective is to gain control of this server and contain the leak.

The file that we're given is a `.tar.gz` file, meaning that it's a tarball that's been gzipped; a tarball is a file format that combines multiple files into a single file, and gzip is a file compression format. We can decompress the gzip and extract the files from the tarball using the `gunzip` and `tar` utilities, additionally passing `xf` (extract file) to `tar` as a command line argument:

```sh
[skat@anubis:~/work/UIUCTF] $ ls
tablet.tar.gz
[skat@anubis:~/work/UIUCTF] $ gunzip tablet.tar.gz
[skat@anubis:~/work/UIUCTF] $ tar xf tablet.tar
[skat@anubis:~/work/UIUCTF] $ ls
private  tablet.tar
```

We can see that we've extracted a new directory: `private/`. We can get oriented by exploring the directory; a great utility is `tree`, which will display a tree structure of the filesystem starting from your current active directory if no additional arguments are supplied.

```sh
[skat@anubis:~/work/UIUCTF] $ cd private/
[skat@anubis:~/work/UIUCTF/private] $ ls
var
[skat@anubis:~/work/UIUCTF/private] $ cd var/
[skat@anubis:~/work/UIUCTF/private/var] $ ls
 buddy        empty     hardware   iomfb_bics_daemon   Keychains   logs                   mobile         MobileSoftwareUpdate   networkd      protected   run                  tmp
 containers   folders   installd   keybags             log        'Managed Preferences'   MobileDevice   msgs                   preferences   root        staged_system_apps   wireless
[skat@anubis:~/work/UIUCTF/private/var] $ tree
.
├── buddy
├── containers
│   ├── Data
│   │   └── System
│   │       ├── 0484B045-1EFD-4EC1-9B74-3E7665974A42
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
│   │       │   └── tmp [error opening dir]
│   │       ├── 1CB5E5B6-3849-4CA0-8DCD-BF5A521286B9
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
│   │       │   └── tmp [error opening dir]
│   │       ├── 28841A8D-11F8-4013-8D5D-B02B63B944F4
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
│   │       │   └── tmp [error opening dir]
│   │       ├── 2FD33CE1-DDAD-4FEC-A4F5-55144CBA75EB
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
│   │       │   └── tmp [error opening dir]
│   │       ├── 416AB7BD-5EC1-4075-9704-44048CF01074
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
│   │       │   └── tmp [error opening dir]
│   │       ├── 4BA18D97-352A-475E-9C22-36315FF4C868
│   │       │   ├── Documents [error opening dir]
│   │       │   ├── Library [error opening dir]
-- snip --
```

Whoa, that's a lot of information to take in! In fact, `tree`'s output goes on for 12,541 lines in total. This is common in any digital forensics investigation: you're given such a great quantity of information that it would be impractical to go through every single one individually, so you must be smart and precise about how you select certain pieces of evidence such that you make good use of your time while also not compromising the value of the information that you do uncover. We'll get back to this in a moment.

Before we dig too deep into the investigation itself, we can see that there are a bunch of errors in opening up directories according to the output of `tree`. Let's select a sample one, `./containers/Data/System/0484B045-1EFD-4EC1-9B74-3E7665974A42/Documents/`, and find out why we're having trouble opening up these directories:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ ls ./containers/Data/System/0484B045-1EFD-4EC1-9B74-3E7665974A42/Documents/
ls: cannot open directory './containers/Data/System/0484B045-1EFD-4EC1-9B74-3E7665974A42/Documents/': Permission denied
[skat@anubis:~/work/UIUCTF/private/var] $ ls -l ./containers/Data/System/0484B045-1EFD-4EC1-9B74-3E7665974A42/
total 12
d--------- 2 skat skat 4096 Jul 23 10:36 Documents
d--------- 4 skat skat 4096 Jul 23 10:36 Library
d--------- 2 skat skat 4096 Jul 23 10:36 tmp
```

Of course we can't access anything -- [the modes](https://github.com/shawnduong/zero-to-hero-hacking/blob/master/linux/permissions-and-modes.md) are insufficient for read access! In fact, we have neither read, write, nor execution permissions. We can solve all of these problems at once by giving ourselves all three permissions for all files and directories in the backup, which can easily be done recursively with `chmod -R`:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ chmod -R 700 *
[skat@anubis:~/work/UIUCTF/private/var] $ tree
.
├── buddy
├── containers
│   ├── Data
│   │   └── System
│   │       ├── 0484B045-1EFD-4EC1-9B74-3E7665974A42
│   │       │   ├── Documents
│   │       │   ├── Library
│   │       │   │   ├── Caches
│   │       │   │   └── Preferences
│   │       │   └── tmp
│   │       ├── 1CB5E5B6-3849-4CA0-8DCD-BF5A521286B9
│   │       │   ├── Documents
│   │       │   ├── Library
│   │       │   │   ├── Caches
│   │       │   │   └── Preferences
│   │       │   └── tmp
│   │       ├── 28841A8D-11F8-4013-8D5D-B02B63B944F4
│   │       │   ├── Documents
│   │       │   ├── Library
│   │       │   │   ├── Caches
│   │       │   │   │   ├── functions.data
│   │       │   │   │   ├── functions.list
│   │       │   │   │   ├── libraries.data
│   │       │   │   │   └── libraries.list
│   │       │   │   └── Preferences
│   │       │   └── tmp
│   │       ├── 2FD33CE1-DDAD-4FEC-A4F5-55144CBA75EB
│   │       │   ├── Documents
│   │       │   ├── Library
│   │       │   │   ├── Caches
│   │       │   │   └── Preferences
│   │       │   └── tmp
│   │       ├── 416AB7BD-5EC1-4075-9704-44048CF01074
-- snip --
```

Great, no more errors! Based on the briefing earlier, we know that we currently have a backup of Red's tablet. Before we start combing through the files, let's see if we can first find out what type of tablet Red has. Knowing what type of device we're investigating may help us locate things and orient ourselves much more effectively.

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ ls
 buddy        empty     hardware   iomfb_bics_daemon   Keychains   logs                   mobile         MobileSoftwareUpdate   networkd      protected   run                  tmp
 containers   folders   installd   keybags             log        'Managed Preferences'   MobileDevice   msgs                   preferences   root        staged_system_apps   wireless
```

`hardware/` looks interesting.

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ tree hardware
hardware
└── FactoryData
    └── System
        └── Library
            └── Caches
                ├── apticket.der
                └── com.apple.factorydata
                    ├── ccrt-00008000-000007B6C93ED5F9
                    ├── FSCl-F58717371LRHGXG8BB
                    ├── hop0-F58717371LRHGXG8BB
                    ├── NvMR-F58717371LRHGXG8BB
                    ├── pcrt-e245a4599e9b3fb42f334fc4b1c4cb3509582869
                    ├── scrt-00008000-000007B6C93ED5F9
                    ├── seal-00008000-000007B6C93ED5F9
                    └── trustobject-5340B6A059BDB732E715E7BB1B292EDCD45C2A8D1D07E6039D3F338D7C4428AB
```

Just like that, we now know that we're on an Apple system. Apple's line of tablets are iPads, so we can safely assume that this is an Apple iPad. This gives us a starting point from which we can do our research from.

It's always important to get oriented when dealing with a new set of data. By first understanding that we're dealing with an iPad device that's running iPadOS, we can better and more precisely inspect the system while keeping in mind that its behavior will be that of an iPadOS; this removes an element of unpredictability from the equation.

According to Wikipedia's article on [iPadOS](https://web.archive.org/web/20210728223925/https://en.wikipedia.org/wiki/IPadOS), iPadOS is a rebranded variant of iOS. [iPadOS 14](https://web.archive.org/web/20210728224854/https://en.wikipedia.org/wiki/IPadOS_14), the current major release of iPadOS, seems to at least partially mirror the features of iOS 14. Although we're not sure if this specific backup is of an iPadOS 14 device, we can at least make the educated assumption that vital features and internal workings may stay consistent; our research on iPadOS 14 and iOS 14 may still be relevant to whatever specific operating system is on the device being investigated. Doing more research on what type of filesystem is utilized by iOS 14 brings us to an article from Apple's own documentation: ["File System Basics."](https://web.archive.org/web/20210604045749/https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html)

Because we know that Red had exfiltrated data to a private server, knowing the tools that Red may have used may reveal where this private server is, how Red communicated with this server, and how Red may have connected to this server. What we're looking for is a host, either in the form of a domain or an IP address, within the data of some application.

The aforementioned official Apple documentation tells us something important:

> For security purposes, an iOS app’s interactions with the file system are limited to the directories inside the app’s sandbox directory. During installation of a new app, the installer creates a number of container directories for the app inside the sandbox directory.

We're targeting applications that Red may have used to exfiltrate data since we're searching for the potential host that Red may have connected to. Applications on an iOS device -- and by extension, most likely on an iPadOS device -- have their files confined to containers for security reasons. Let's find where these containers are located using `find`:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ find . -name "Containers"
./mobile/Containers
```

Let's navigate to the containers and get oriented using `tree`:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ cd ./mobile/Containers/
[skat@anubis:~/work/UIUCTF/private/var/mobile/Containers] $ tree
.
├── Data
│   ├── Application
│   │   ├── 0086F008-29FB-4F0A-AEF7-2EA84DBCE5BD
│   │   │   ├── Documents
│   │   │   ├── Library
│   │   │   │   ├── Caches
│   │   │   │   └── Preferences
│   │   │   ├── SystemData
│   │   │   └── tmp
│   │   ├── 009B0AA6-834F-433E-A1CC-D573DE8ADF6F
│   │   │   ├── Documents
│   │   │   ├── Library
│   │   │   │   ├── Caches
│   │   │   │   ├── Preferences
│   │   │   │   └── SplashBoard
│   │   │   │       └── Snapshots
│   │   │   │           └── com.apple.dt.XcodePreviews - {DEFAULT GROUP}
│   │   │   │               ├── 080464E1-D42F-4D8E-9D2D-8C18BE42C874@2x.ktx
│   │   │   │               ├── 194C4475-1EA1-495D-8B00-A06FA13EB212@2x.ktx
│   │   │   │               ├── 1D2FF3B4-E656-4976-A8B8-C3EAB7BF29AE@2x.ktx
│   │   │   │               ├── 38B8C5FD-456B-4972-AE04-CCEFFB738EE8@2x.ktx
│   │   │   │               ├── 5F090246-FD8E-4477-8834-4F094A0CE129@2x.ktx
│   │   │   │               ├── 90CFFFF1-DB89-447A-98B7-3190F4DCC26F@2x.ktx
│   │   │   │               ├── 9144A369-E7C7-4CF2-8B73-9A7ECEBFBBB6@2x.ktx
│   │   │   │               └── D43458C6-E992-4780-A5E3-F68F8B25EC5A@2x.ktx
│   │   │   ├── SystemData
│   │   │   └── tmp
│   │   ├── 05AB72AC-91C4-4A63-9116-D5C43068EA5F
│   │   │   ├── Documents
│   │   │   ├── Library
│   │   │   │   ├── Caches
│   │   │   │   ├── Preferences
│   │   │   │   └── SplashBoard
│   │   │   │       └── Snapshots
│   │   │   │           └── com.apple.WebSheet - {DEFAULT GROUP}
-- snip --
```

7,474 lines of output! We don't really care about most of these files, but we do know now where the apps are located. Let's try to get a list of all apps that are available on this system. Something that you may have noticed is that apps have names such as `com.apple.dt.XcodePreviews` and `com.apple.WebSheet`, something known was **reverse domain name notation.** We can use this to our advantage to create an expression that will only give us directories or files with an app name since we know that it will most likely start with some sort of common top-level domain like ".com" or ".org." Let's `find` these:

```sh
[skat@anubis:~/work/UIUCTF/private/var/mobile/Containers] $ find . -name "com.*"
./Data/PluginKitPlugin/6C4CE4A9-900B-4177-B7EA-770F4DCE7C57/SystemData/com.apple.chrono
./Data/PluginKitPlugin/6C4CE4A9-900B-4177-B7EA-770F4DCE7C57/SystemData/com.apple.chrono/placeholders/com.apple.Maps
./Data/PluginKitPlugin/6C4CE4A9-900B-4177-B7EA-770F4DCE7C57/Library/Caches/com.apple.dyld
./Data/PluginKitPlugin/9CEFB254-EACD-409A-ADD6-F526CDE241DD/Library/Caches/com.apple.Animoji.StickersApp.MessagesExtension
./Data/PluginKitPlugin/9CEFB254-EACD-409A-ADD6-F526CDE241DD/Library/Caches/com.apple.Animoji.StickersApp.MessagesExtension/com.apple.metalfe
./Data/PluginKitPlugin/9CEFB254-EACD-409A-ADD6-F526CDE241DD/Library/Caches/com.apple.Animoji.StickersApp.MessagesExtension/com.apple.metal
./Data/PluginKitPlugin/26BC37DE-ECA3-4DE2-83FD-BB19CC960116/Library/SyncedPreferences/com.apple.kvs
./Data/PluginKitPlugin/26BC37DE-ECA3-4DE2-83FD-BB19CC960116/Library/SyncedPreferences/com.apple.kvs/ChangeTokens/EndToEndEncryption/WeatherIntents/com.apple.weather
./Data/PluginKitPlugin/26BC37DE-ECA3-4DE2-83FD-BB19CC960116/Library/SyncedPreferences/com.apple.weather.WeatherIntents.plist
./Data/PluginKitPlugin/E00F3026-1873-4BF6-BE3E-1E10F75FEB71/Library/SyncedPreferences/com.apple.mobilenotes.SharingExtension-com.apple.notes.analytics.plist
./Data/PluginKitPlugin/E00F3026-1873-4BF6-BE3E-1E10F75FEB71/Library/SyncedPreferences/com.apple.mobilenotes.SharingExtension.plist
./Data/PluginKitPlugin/4DCDF246-E707-4F52-B616-39B0BB323238/SystemData/com.apple.chrono
./Data/PluginKitPlugin/4DCDF246-E707-4F52-B616-39B0BB323238/SystemData/com.apple.chrono/placeholders/com.apple.tips
./Data/PluginKitPlugin/4DCDF246-E707-4F52-B616-39B0BB323238/Library/Caches/com.apple.dyld
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/SystemData/com.apple.chrono
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/SystemData/com.apple.chrono/placeholders/com.apple.mobilenotes.FolderWidget
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/SystemData/com.apple.chrono/placeholders/com.apple.mobilenotes.NoteWidget
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/Library/Caches/com.apple.dyld
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/Library/Caches/com.apple.dyld/com.apple.mobilenotes.WidgetExtension.closure
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/Library/SyncedPreferences/com.apple.mobilenotes.WidgetExtension-com.apple.notes.analytics.plist
./Data/PluginKitPlugin/B3D150FB-FD7E-4A6D-A4B0-C8277CADF6DF/Library/SyncedPreferences/com.apple.mobilenotes.WidgetExtension.plist
./Data/PluginKitPlugin/09D88789-E428-4922-B8D9-802A7399F256/Library/Preferences/com.apple.FileProvider
./Data/PluginKitPlugin/09D88789-E428-4922-B8D9-802A7399F256/Library/Preferences/com.apple.FileProvider/com.apple.CloudDocs.MobileDocumentsFileProvider
./Data/PluginKitPlugin/D02660B1-0F69-424C-B13C-AB0D17D1D979/SystemData/com.apple.chrono
./Data/PluginKitPlugin/D02660B1-0F69-424C-B13C-AB0D17D1D979/SystemData/com.apple.chrono/placeholders/com.apple.tv
-- snip --
```

Alright, that's still a lot to take in! Let's use `awk` to split each line by the `/` delimiter and print only the final token containing the name, and then let's `sort` it and make a unique list out of it with `uniq -u`. Let's additionally filter out all the built-in Apple stuff by performing a reverse `grep` on the "com.apple" string:

```sh
[skat@anubis:~/.../Containers] $ find . -name "com.*" | awk -F '/' '{print $NF}' | sort | uniq -u | grep -v "com.apple"
com.crashlytics
com.crashlytics.data
com.firebase.FIRInstallations.plist
com.google.gmp.measurement.monitor.plist
com.google.gmp.measurement.plist
com.hackemist.SDImageCache
com.hammerandchisel.discord - {DEFAULT GROUP}
com.hammerandchisel.discord.plist
com.hammerandchisel.discord.savedState
com.innersloth.amongus - {DEFAULT GROUP}
com.innersloth.amongus.plist
com.innersloth.amongus.savedState
com.itimeteo.webssh - {DEFAULT GROUP}
com.itimeteo.webssh.plist
com.itimeteo.webssh.savedState
com.plausiblelabs.crashreporter.data
```

Awesome! Right away, I notice `com.itimeteo.webssh`. Could Red have been using SSH to exfiltrate data? Let's find out by continuing to explore this application and its associated saved data:

```sh
[skat@anubis:~/work/UIUCTF/private/var/mobile/Containers] $ find . -name "com.itimeteo.webssh - {DEFAULT GROUP}"
./Data/Application/AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B/Library/SplashBoard/Snapshots/com.itimeteo.webssh - {DEFAULT GROUP}
[skat@anubis:~/work/UIUCTF/private/var/mobile/Containers] $ cd ./Data/Application/AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B/
[skat@anubis:~/work/UIUCTF/private/var/mobile/Containers/Data/Application/AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B] $ tree
.
├── Documents
├── Library
│   ├── Application Support
│   │   └── webssh.db
│   ├── Caches
│   │   └── com.apple.dyld
│   │       └── WebSSH.closure
│   ├── Preferences
│   │   └── com.itimeteo.webssh.plist
│   ├── Saved Application State
│   │   └── com.itimeteo.webssh.savedState
│   │       └── KnownSceneSessions
│   │           └── data.data
│   └── SplashBoard
│       └── Snapshots
│           ├── com.itimeteo.webssh - {DEFAULT GROUP}
│           │   ├── 14838935-9A83-4B7A-A340-E662593C666E@2x.ktx
│           │   ├── 3D6E2704-7354-4728-9686-67B626541EFE@2x.ktx
│           │   ├── 68B31944-676B-47CF-B1FC-C5C0B190AC16@2x.ktx
│           │   ├── 89B3C356-395B-4D8F-AFB4-05D32CB5409A@2x.ktx
│           │   ├── 9F8D3DA2-FDA7-4EB3-981D-514D277F1E85@2x.ktx
│           │   ├── A06B3B88-1384-41D6-8C49-AC4A1C9964B2@2x.ktx
│           │   ├── A1F7241A-C71F-430B-969E-7E627FC22F53@2x.ktx
│           │   ├── B3AA04CC-C35A-420E-9F83-ACA0EA306207@2x.ktx
│           │   └── downscaled
│           │       └── 788735BD-3AA3-481E-A60B-F318C5C5C678@2x.ktx
│           └── sceneID:com.itimeteo.webssh-default
│               └── downscaled
├── StoreKit
│   └── receipt
├── SystemData
└── tmp

18 directories, 14 files
```

I see a `webssh.db` file, which seems interesting. Perhaps this file will contain some saved data regarding Red's data exfiltration?

```sh
[skat@anubis:~/.../AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B] $ cd "./Library/Application Support"
[skat@anubis:~/.../Application Support] $ file webssh.db
webssh.db: SQLite 3.x database, last written using SQLite version 3032003
[skat@anubis:~/.../Application Support] $ sqlite3 webssh.db
```

```sql
SQLite version 3.36.0 2021-06-18 18:36:39
Enter ".help" for usage hints.
sqlite> .dump
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE NSFValues(ROWID INTEGER PRIMARY KEY, NSFKey TEXT, NSFAttribute TEXT, NSFValue NONE, NSFDatatype TEXT);
INSERT INTO NSFValues VALUES(1,'4F479229-163D-469B-AD21-E23CDFDAFBBC','privatePart',replace('-----BEGIN OPENSSH PRIVATE KEY-----\n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\n9HmS+uFZxtacdqj4KdrHPcagm3Q=\n-----END OPENSSH PRIVATE KEY-----\n','\n',char(10)),'TEXT');
INSERT INTO NSFValues VALUES(2,'4F479229-163D-469B-AD21-E23CDFDAFBBC','objectIsDeleted',0,'REAL');
INSERT INTO NSFValues VALUES(3,'4F479229-163D-469B-AD21-E23CDFDAFBBC','objectCreation','2021-07-25 14:12:28:733','TEXT');
INSERT INTO NSFValues VALUES(4,'4F479229-163D-469B-AD21-E23CDFDAFBBC','objectType','privateKey','TEXT');
INSERT INTO NSFValues VALUES(5,'4F479229-163D-469B-AD21-E23CDFDAFBBC','objectEdition','2021-07-25 14:12:28:739','TEXT');
INSERT INTO NSFValues VALUES(6,'4F479229-163D-469B-AD21-E23CDFDAFBBC','isEncrypted',1,'REAL');
INSERT INTO NSFValues VALUES(7,'4F479229-163D-469B-AD21-E23CDFDAFBBC','name','private_key','TEXT');
INSERT INTO NSFValues VALUES(8,'4F479229-163D-469B-AD21-E23CDFDAFBBC','decryptPassword','********','TEXT');
INSERT INTO NSFValues VALUES(9,'69933883-557F-4A3D-94ED-F38CEE706B57','objectCreation','2021-07-25 14:11:08:530','TEXT');
INSERT INTO NSFValues VALUES(10,'69933883-557F-4A3D-94ED-F38CEE706B57','port_knocking','','TEXT');
INSERT INTO NSFValues VALUES(11,'69933883-557F-4A3D-94ED-F38CEE706B57','objectType','connection','TEXT');
INSERT INTO NSFValues VALUES(12,'69933883-557F-4A3D-94ED-F38CEE706B57','port_forwarding','','TEXT');
INSERT INTO NSFValues VALUES(13,'69933883-557F-4A3D-94ED-F38CEE706B57','type','SSH','TEXT');
INSERT INTO NSFValues VALUES(14,'69933883-557F-4A3D-94ED-F38CEE706B57','host','red.chal.uiuc.tf','TEXT');
INSERT INTO NSFValues VALUES(15,'69933883-557F-4A3D-94ED-F38CEE706B57','objectIsDeleted',0,'REAL');
INSERT INTO NSFValues VALUES(16,'69933883-557F-4A3D-94ED-F38CEE706B57','authentication.privateKeyID','4F479229-163D-469B-AD21-E23CDFDAFBBC','TEXT');
INSERT INTO NSFValues VALUES(17,'69933883-557F-4A3D-94ED-F38CEE706B57','authentication.password','','TEXT');
INSERT INTO NSFValues VALUES(18,'69933883-557F-4A3D-94ED-F38CEE706B57','authentication.2fa','false','TEXT');
INSERT INTO NSFValues VALUES(19,'69933883-557F-4A3D-94ED-F38CEE706B57','authentication.user','red','TEXT');
INSERT INTO NSFValues VALUES(20,'69933883-557F-4A3D-94ED-F38CEE706B57','groupName','','TEXT');
INSERT INTO NSFValues VALUES(21,'69933883-557F-4A3D-94ED-F38CEE706B57','objectEdition','2021-07-25 14:12:31:621','TEXT');
INSERT INTO NSFValues VALUES(22,'69933883-557F-4A3D-94ED-F38CEE706B57','name','Red’s Server','TEXT');
INSERT INTO NSFValues VALUES(23,'69933883-557F-4A3D-94ED-F38CEE706B57','port',42069,'REAL');
CREATE TABLE NSFKeys(ROWID INTEGER PRIMARY KEY, NSFKey TEXT, NSFKeyedArchive BLOB, NSFCalendarDate TEXT, NSFObjectClass TEXT);
INSERT INTO NSFKeys VALUES(1,'4F479229-163D-469B-AD21-E23CDFDAFBBC',X'62706c6973743030d4010203040506070a582476657273696f6e592461726368697665725424746f7058246f626a6563747312000186a05f100f4e534b657965644172636869766572d1080954726f6f748001af10150b0c232425262728292a2b2f37383c3f404344454655246e756c6cd30d0e0f101922574e532e6b6579735a4e532e6f626a656374735624636c617373a8111213141516171880028003800480058006800780088009a81a1b1c1d1e1f2021800a800c800d800f801080118012801380145b70726976617465506172745f100f6f626a656374497344656c657465645e6f626a6563744372656174696f6e5a6f626a656374547970655d6f626a65637445646974696f6e5b6973456e63727970746564546e616d655f100f6465637279707450617373776f7264d20f2c2d2e594e532e737472696e67800b5f110a5f2d2d2d2d2d424547494e204f50454e5353482050524956415445204b45592d2d2d2d2d0a6233426c626e4e7a614331725a586b74646a454141414141436d466c637a49314e69316a6448494141414147596d4e796558423041414141474141414142417471656d704e770a54757772456d706c2b4379325178414141414541414141414541414147584141414142334e7a614331796332454141414144415141424141414267514443347576474b72314d0a3335695a4a6b4255356b4b64754b74424d45467569344a61726b567575444d79307337676b554e353443517a522b70544735755050422f32416f4770413942452f35585258690a654f624b4a71656d784250646655412f5a6c436b66377543736d59354262424253633764504e566741556843654249324a59482f72434b4b51346870574854595242695537590a6b3454394e736b367273495a4b76546e7652462b355a5371466a5941776c7a66662b4567627342675163306b37356a4869456f697564696e596d376b7771454d6e7a585961380a7065725074756b4a3351614f6a67505036744f53443450305837417863732b5537704261505a734e47445931352f517a49523466533479523332696d596a4a314831376e31550a4577344b787146696e70742f71475a54476a6e68454866486641575276776e51346e566972624953556c69757872704d654533766b776c4d63767735554a567a45445a4239380a5852785a577a76647359526a6c577571686150743559674a6858312b334e45306f47484443564d6d6478506453734c38736b6b654d6d4b4f62356b3530455a3165413558462f0a592f782f72434d657171563375773661574e65383876694d67336941542f4234644e3763495330574b582b3267637642506e395a787934587532705341714b6375524a2b544c0a4c76695232386879336c7a4c73414141575141585355506d665777426a45637a4e642f68504765374f376a387a392f676153744d42672b724a57745632446d313836304162680a4e2f756a3244533354486d324f444c6c676b4561634943596733506c776676794b734a447738364c63376b4f552b6a2b774d514c6f536a3545396c59716d4e636f426c5472750a43695577396f53656f65562f527a5175594a3277354447382f5636554669586e5944755457304b6b38792f6c34556a2b397a5367556f68336b666b52484f69763167456a46580a694b78522b2f516b51316f414a6b73343944445833373375746d62685a362f67474762476b46796c4d44654d6b6458773061655449365558306842354479477a31535172476b0a62545a7a5057674d6a7456574a593077764d36617277735431637131736745596a706f57574f66663042514f425578564157333336593248414559702f7a734d434c4c335a6f0a772f36664f6a2b65705272713030525037496c6e556a51433242333871674362496c6c61664f7455525659427835776a4e444e557038644474325852455130687338792b55790a2f3936414b524f53412f506a317a2f36786a774c4171576a67537879694d5770524a504b645371664e444c716d7779753845662f456e743053574c58594b38475043567236580a746a487447522b7376716c3879553034526f4f476949564733517a545a345777444f764568525741307a414841754f756c6371776d3843776c76385a5053303555716f4750780a5634756e3367324454735766614d6536744846715654624e756d756d55615a4c336b47705649634e4a4b6d436e70324650716f3336644b76473256684f4c45714d61476c50760a464158747678714c697a394d54314b72345758795263706d3473316f7934633572685371326f77445a4377516e744d423034724878596b47642b5278616a6f56466473352b630a555a38376f7578322f30623052572f6357423273427a7673545a4d6938573935344b6f4a39644e614957394b2f3461314e4c6a354a594146354a6832513950566369464f78700a6f6953534f41664d71544f5267357a7a2f435337624f35496a59344c63576b31394a4d396d344f32394f6976424f6c5269426a366d42506e66576e6f327668554a6565624c480a3376496a5767654c45564c7639666b4f5a39727332652b5266444d4f5734474154674f68566275436a747143684348585247416c69784c2b4a653147785142673578712f414e0a67383965777a4d324f7539352b4c7745414d7578664c666a33306468417634374c416c4f59762f7a36686d4a41634842654f417568744177744277564832415333586d42717a0a74774668433362575a374f4150625777426a557a63736a326e3776486c72515274426a71302b7a2f4b4a334d442b4574504a362f706f647a343579507173794e364a6b4c63410a4e45562b4a4b6434706b515a6143336d524648416b47334b56344b355753434246546436434c724461557a5357306c31485a4d704a665267623348445642496f7337676e64570a316b416b794b41463672643744717175334a555a37654768777a453138425a71473051507846392f3132326369743376476a4a434f56653865384936446a5a6d5179773867610a4859463634465a61696b7853316333586464686a3857485253776650522b384e437243386457423632427a32394a6f51584c6a393847564738484376347749743145734159330a726669726832364151456c326d506d72776554793152766c75514c4f4b46594a546864713464726e4b6434575150734c4b37756d6833697a616861777631633466374f6c4b480a4d6371766a50667768337165674870704c5577464a5747772f6350314c45332f6a6a6d504a61727071612f376d306437344d33434164596f6f37704d516954634973625634640a2b672b30722f44673269554d6e2f7a45746b653055774d4147326347794e53472b47534243374556547248394332747a55372f6a5046595538753459314934414846617168520a744f72716d2f5541454e64666e427167376b6f6458312f68326c457573546939686b715a5a454d616f4b71456a574d596943764a382b744c707678304f7373314a77514536560a4c335175752b7659635173397843766f4e77304e41716f453262704970464a6530524a6c332b362b47654a437574384830396d366862477a46777157736f564b304c685435410a4b344344774b4933706f426c4b59574758567344426557496439724f69367248706c5965772b502b7773344d6c6453626732516e59626e2f67644c51334a643549494a38782b0a524c6a454b62524a39622b7243544f6951355254577034354b2f71327134753650326b6c51775232455537425633324e6c2b5a6576445a556e56516c4d4937735769747a47460a4f6563346b332f5649633642516338755a34744148304d50696645566f7847316d5a7832767466456351546a4b4c4b627773574b6c4c4d374c41674665335a444a38616965620a7176627843376e6b76694d534c4955775a517a76575243542b7766662f2f776767594942722f4579746346714a633346306539715455763372336168614777493857326732790a39486d532b75465a7874616364716a344b647248506361676d33513d0a2d2d2d2d2d454e44204f50454e5353482050524956415445204b45592d2d2d2d2d0ad2303132335a24636c6173736e616d655824636c61737365735f100f4e534d757461626c65537472696e67a33435365f100f4e534d757461626c65537472696e67584e53537472696e67584e534f626a65637408d2390f3a3b574e532e74696d652341c356f78e5dcc53800ed230313d3e564e5344617465a23d365a707269766174654b6579d2390f413b2341c356f78e5e9b63800e095b707269766174655f6b6579582a2a2a2a2a2a2a2ad2303147485f10134e534d757461626c6544696374696f6e617279a34749365c4e5344696374696f6e61727900080011001a00240029003200370049004c00510053006b007100780080008b0092009b009d009f00a100a300a500a700a900ab00b400b600b800ba00bc00be00c000c200c400c600d200e400f300fe010c0118011d012f0134013e01400ba30ba80bb30bbc0bce0bd20be40bed0bf60bf70bfc0c040c0d0c0f0c140c1b0c1e0c290c2e0c370c390c3a0c460c4f0c540c6a0c6e0000000000000201000000000000004a00000000000000000000000000000c7b','2021-07-25 14:12:28:750','BO');
INSERT INTO NSFKeys VALUES(2,'69933883-557F-4A3D-94ED-F38CEE706B57',X'62706c6973743030d4010203040506070a582476657273696f6e592461726368697665725424746f7058246f626a6563747312000186a05f100f4e534b657965644172636869766572d1080954726f6f748001af10220b0c2b2c2d2e2f30313233343536373b41424344454652535455565758595a5e616255246e756c6cd30d0e0f101d2a574e532e6b6579735a4e532e6f626a656374735624636c617373ac1112131415161718191a1b1c80028003800480058006800780088009800a800b800c800dac1e1f201f222324251f272829800e80108011801080128013801480158010801f80208021801e5e6f626a6563744372656174696f6e5d706f72745f6b6e6f636b696e675a6f626a656374547970655f100f706f72745f666f7277617264696e67547479706554686f73745f100f6f626a656374497344656c657465645e61757468656e7469636174696f6e5967726f75704e616d655d6f626a65637445646974696f6e546e616d6554706f7274d2380f393a574e532e74696d652341c356f76643dfb1800fd23c3d3e3f5a24636c6173736e616d655824636c6173736573564e5344617465a23e40584e534f626a656374505a636f6e6e656374696f6e535353485f10107265642e6368616c2e756975632e746608d30d0e0f474c2aa448494a4b8016801780188019a44d4e4f50801a801b801c801d801e5c707269766174654b657949445870617373776f72645332666154757365725f102434463437393232392d313633442d343639422d414432312d453233434446444146424243505566616c736553726564d23c3d5b5c5f10134e534d757461626c6544696374696f6e617279a35b5d405c4e5344696374696f6e617279d2380f5f3a2341c356f78fcf8898800f6c00520065006420190073002000530065007200760065007211a45500080011001a00240029003200370049004c005100530078007e0085008d0098009f00ac00ae00b000b200b400b600b800ba00bc00be00c000c200c400d100d300d500d700d900db00dd00df00e100e300e500e700e900eb00fa010801130125012a012f01410150015a0168016d01720177017f0188018a018f019a01a301aa01ad01b601b701c201c601d901da01e101e601e801ea01ec01ee01f301f501f701f901fb01fd020a02130217021c02430244024a024e02530269026d027a027f0288028a02a300000000000002010000000000000063000000000000000000000000000002a6','2021-07-25 14:12:31:629','ConnectionBO');
COMMIT;
```

Well, would you look at that!

```sql
INSERT INTO NSFValues VALUES(14,'69933883-557F-4A3D-94ED-F38CEE706B57','host','red.chal.uiuc.tf','TEXT');
INSERT INTO NSFValues VALUES(23,'69933883-557F-4A3D-94ED-F38CEE706B57','port',42069,'REAL');
INSERT INTO NSFValues VALUES(19,'69933883-557F-4A3D-94ED-F38CEE706B57','authentication.user','red','TEXT');
INSERT INTO NSFValues VALUES(1,'4F479229-163D-469B-AD21-E23CDFDAFBBC','privatePart',replace('-----BEGIN OPENSSH PRIVATE KEY-----\n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\n9HmS+uFZxtacdqj4KdrHPcagm3Q=\n-----END OPENSSH PRIVATE KEY-----\n','\n',char(10)),'TEXT');
INSERT INTO NSFValues VALUES(8,'4F479229-163D-469B-AD21-E23CDFDAFBBC','decryptPassword','********','TEXT');
```

We have a host, port, username, SSH private key, and the decryption password -- five ingredients for an SSH connection! I must admit that I found the decryption password to be quite humorous; I initially thought that the password must have been censored, but it is actually, literally `********`.

Let's go ahead and copy that SSH private key into a file, give it the appropriate permissions, and connect to the server that we just uncovered. This is an exciting development!

```sh
[skat@anubis:~/work/UIUCTF] $ cat key
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABAtqempNw
TuwrEmpl+Cy2QxAAAAEAAAAAEAAAGXAAAAB3NzaC1yc2EAAAADAQABAAABgQDC4uvGKr1M
35iZJkBU5kKduKtBMEFui4JarkVuuDMy0s7gkUN54CQzR+pTG5uPPB/2AoGpA9BE/5XRXi
eObKJqemxBPdfUA/ZlCkf7uCsmY5BbBBSc7dPNVgAUhCeBI2JYH/rCKKQ4hpWHTYRBiU7Y
k4T9Nsk6rsIZKvTnvRF+5ZSqFjYAwlzff+EgbsBgQc0k75jHiEoiudinYm7kwqEMnzXYa8
perPtukJ3QaOjgPP6tOSD4P0X7Axcs+U7pBaPZsNGDY15/QzIR4fS4yR32imYjJ1H17n1U
Ew4KxqFinpt/qGZTGjnhEHfHfAWRvwnQ4nVirbISUliuxrpMeE3vkwlMcvw5UJVzEDZB98
XRxZWzvdsYRjlWuqhaPt5YgJhX1+3NE0oGHDCVMmdxPdSsL8skkeMmKOb5k50EZ1eA5XF/
Y/x/rCMeqqV3uw6aWNe88viMg3iAT/B4dN7cIS0WKX+2gcvBPn9Zxy4Xu2pSAqKcuRJ+TL
LviR28hy3lzLsAAAWQAXSUPmfWwBjEczNd/hPGe7O7j8z9/gaStMBg+rJWtV2Dm1860Abh
N/uj2DS3THm2ODLlgkEacICYg3PlwfvyKsJDw86Lc7kOU+j+wMQLoSj5E9lYqmNcoBlTru
CiUw9oSeoeV/RzQuYJ2w5DG8/V6UFiXnYDuTW0Kk8y/l4Uj+9zSgUoh3kfkRHOiv1gEjFX
iKxR+/QkQ1oAJks49DDX373utmbhZ6/gGGbGkFylMDeMkdXw0aeTI6UX0hB5DyGz1SQrGk
bTZzPWgMjtVWJY0wvM6arwsT1cq1sgEYjpoWWOff0BQOBUxVAW336Y2HAEYp/zsMCLL3Zo
w/6fOj+epRrq00RP7IlnUjQC2B38qgCbIllafOtURVYBx5wjNDNUp8dDt2XREQ0hs8y+Uy
/96AKROSA/Pj1z/6xjwLAqWjgSxyiMWpRJPKdSqfNDLqmwyu8Ef/Ent0SWLXYK8GPCVr6X
tjHtGR+svql8yU04RoOGiIVG3QzTZ4WwDOvEhRWA0zAHAuOulcqwm8Cwlv8ZPS05UqoGPx
V4un3g2DTsWfaMe6tHFqVTbNumumUaZL3kGpVIcNJKmCnp2FPqo36dKvG2VhOLEqMaGlPv
FAXtvxqLiz9MT1Kr4WXyRcpm4s1oy4c5rhSq2owDZCwQntMB04rHxYkGd+RxajoVFds5+c
UZ87oux2/0b0RW/cWB2sBzvsTZMi8W954KoJ9dNaIW9K/4a1NLj5JYAF5Jh2Q9PVciFOxp
oiSSOAfMqTORg5zz/CS7bO5IjY4LcWk19JM9m4O29OivBOlRiBj6mBPnfWno2vhUJeebLH
3vIjWgeLEVLv9fkOZ9rs2e+RfDMOW4GATgOhVbuCjtqChCHXRGAlixL+Je1GxQBg5xq/AN
g89ewzM2Ou95+LwEAMuxfLfj30dhAv47LAlOYv/z6hmJAcHBeOAuhtAwtBwVH2AS3XmBqz
twFhC3bWZ7OAPbWwBjUzcsj2n7vHlrQRtBjq0+z/KJ3MD+EtPJ6/podz45yPqsyN6JkLcA
NEV+JKd4pkQZaC3mRFHAkG3KV4K5WSCBFTd6CLrDaUzSW0l1HZMpJfRgb3HDVBIos7gndW
1kAkyKAF6rd7Dqqu3JUZ7eGhwzE18BZqG0QPxF9/122cit3vGjJCOVe8e8I6DjZmQyw8ga
HYF64FZaikxS1c3Xddhj8WHRSwfPR+8NCrC8dWB62Bz29JoQXLj98GVG8HCv4wIt1EsAY3
rfirh26AQEl2mPmrweTy1RvluQLOKFYJThdq4drnKd4WQPsLK7umh3izahawv1c4f7OlKH
McqvjPfwh3qegHppLUwFJWGw/cP1LE3/jjmPJarpqa/7m0d74M3CAdYoo7pMQiTcIsbV4d
+g+0r/Dg2iUMn/zEtke0UwMAG2cGyNSG+GSBC7EVTrH9C2tzU7/jPFYU8u4Y1I4AHFaqhR
tOrqm/UAENdfnBqg7kodX1/h2lEusTi9hkqZZEMaoKqEjWMYiCvJ8+tLpvx0Oss1JwQE6V
L3Quu+vYcQs9xCvoNw0NAqoE2bpIpFJe0RJl3+6+GeJCut8H09m6hbGzFwqWsoVK0LhT5A
K4CDwKI3poBlKYWGXVsDBeWId9rOi6rHplYew+P+ws4MldSbg2QnYbn/gdLQ3Jd5IIJ8x+
RLjEKbRJ9b+rCTOiQ5RTWp45K/q2q4u6P2klQwR2EU7BV32Nl+ZevDZUnVQlMI7sWitzGF
Oec4k3/VIc6BQc8uZ4tAH0MPifEVoxG1mZx2vtfEcQTjKLKbwsWKlLM7LAgFe3ZDJ8aieb
qvbxC7nkviMSLIUwZQzvWRCT+wff//wggYIBr/EytcFqJc3F0e9qTUv3r3ahaGwI8W2g2y
9HmS+uFZxtacdqj4KdrHPcagm3Q=
-----END OPENSSH PRIVATE KEY-----
[skat@anubis:~/work/UIUCTF] $ chmod 600 key
[skat@anubis:~/work/UIUCTF] $ ssh -i key -p 42069 red@red.chal.uiuc.tf
Enter passphrase for key 'key':
This service allows sftp connections only.
Connection to red.chal.uiuc.tf closed.
```

Oh, it looks like the server only allows SFTP connections. Given the context of the scenario, that makes sense. No worries, we can just connect using SFTP instead of SSH:

```sh
[skat@anubis:~/work/UIUCTF] $ sftp -i key -P 42069 red@red.chal.uiuc.tf
Enter passphrase for key 'key':
Connected to red.chal.uiuc.tf.
sftp> pwd
Remote working directory: /home/red
sftp> ls -a
.              ..             .bash_history  .bash_logout   .bashrc        .profile
.ssh
```

Alright, we're in! Let's have a look at the Bash history to see if there's anything interesting that Red may have done on this system. We can get files using the `get` command in SFTP:

```sh
sftp> get .bash_history
Fetching /home/red/.bash_history to .bash_history
/home/red/.bash_history                                    100%   31     0.2KB/s   00:00
```

```sh
[skat@anubis:~/work/UIUCTF] $ cat .bash_history
mv /srv/exfiltrated "/srv/..."
```

It looks like the file `/srv/exfiltrated` was renamed to `/src/...`. Let's have a look at that file. We can again get the file using `get`:

```sh
sftp> cd /srv
sftp> ls -a
.    ..   ...
sftp> get ...
Fetching /srv/.../ to ...
Cannot download non-regular file: /srv/.../
```

Oh, it's a directory; the file was actually being moved to a directory.

```sh
sftp> cd ...
sftp> ls
important_data.jpg
sftp> get important_data.jpg
Fetching /srv/.../important_data.jpg to important_data.jpg
/srv/.../important_data.jpg                                100%   43KB  78.0KB/s   00:00
```

Awesome, some important data! Let's have a look at it:

![](/uploads/2021-08-07/important_data.jpg)

Just like that, we have a flag!

<h3 id="debriefing-1">Debriefing</h3>

We were initially given a backup of Red's tablet and told that Red had been exfiltrating data to a private server; our objective was to access the server and contain the leak. We first got oriented and discovered what type of device it was: an iPad. From here, we began doing research and discovered that iPads use iPadOS, a variant of iOS, whose filesystem structure is [documented by Apple.](https://web.archive.org/web/20210604045749/https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html) Learning that applications on an iOS device run inside of containers, we discover the location of the containers and generate a list of applications present on the device. We found that there was an SSH client and looked through the stored application data to discover a host, port, username, SSH private key, and the decryption password, allowing us to then connect to the server via SFTP, look through the Bash history, and retrieve the exfiltrated data.

Although this was just a CTF challenge, the entire process very closely resembles an operation that could very well happen in real-life operations! Digital forensics is simply just the branch of forensic science involved with digital devices. It lends itself to criminal investigations by focusing on the investigation of digital devices, allowing evidence to be attributed to suspects, incriminating data to be recovered, and more. I oftentimes playfully refer to digital forensics as being like a "hacker detective." This challenge was a great exercise of the digital forensics process: given data, assess the situation and look for evidence of criminal activity on the digital device. Being just a CTF challenge, we could have some fun and also additionally hack into the remote server while avoiding the legal and bureaucratic process that would have otherwise been required as a prerequisite to such an act in a real-life investigation.

## forensics/Tablet 2

*Challenge written by WhiteHoodHacker.*

> Wait... there are TWO impostors?! Red must have been in contact with the other impostor. See if you can find out what they are plotting.

Files: [`tablet.tar.gz`](/uploads/2021-08-07/tablet.tar.gz)

Checksum (SHA-1):

```
27dfb3448130b5e4f0f73a51d2a41b32fd81b284  tablet.tar.gz
```

Looks like this is a development to our initial investigation! Based on this description, let's get our situation oriented:

- There's another impostor that Red's been in contact with.
- Our objective is to find out what they're plotting.

Immediately, my mind jumps to SMS text messages. Let's find out where SMS text messages are located on the tablet:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ find . -name "SMS"
./mobile/Library/SMS
[skat@anubis:~/work/UIUCTF/private/var] $ cd mobile/Library/SMS/
[skat@anubis:~/work/UIUCTF/private/var/mobile/Library/SMS] $ ls
CloudKitMetaData  PluginMetaDataCache  transferInfo                               prewarm.db      prewarm.db-wal  sms.db-shm
Drafts            StickerCache         com.apple.messages.geometrycache_v5.plist  prewarm.db-shm  sms.db          sms.db-wal
```

`sms.db` looks interesting. Let's access and dump that database, just like we dumped an application's database in **forensics/Tablet 1** earlier:

```sh
[skat@anubis:~/work/UIUCTF/private/var/mobile/Library/SMS] $ sqlite3 sms.db
```

```sql
SQLite version 3.36.0 2021-06-18 18:36:39
Enter ".help" for usage hints.
qlite> .dump
earlieAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE _SqliteDatabaseProperties (key TEXT, value TEXT, UNIQUE(key));
INSERT INTO _SqliteDatabaseProperties VALUES('counter_in_all','0');
INSERT INTO _SqliteDatabaseProperties VALUES('counter_out_all','0');
INSERT INTO _SqliteDatabaseProperties VALUES('counter_in_lifetime','0');
INSERT INTO _SqliteDatabaseProperties VALUES('counter_out_lifetime','0');
INSERT INTO _SqliteDatabaseProperties VALUES('counter_last_reset','0');
INSERT INTO _SqliteDatabaseProperties VALUES('_ClientVersion','14006');
INSERT INTO _SqliteDatabaseProperties VALUES('__CSDBRecordSequenceNumber','175');
CREATE TABLE deleted_messages (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, guid TEXT NOT NULL);
CREATE TABLE chat_handle_join (chat_id INTEGER REFERENCES chat (ROWID) ON DELETE CASCADE, handle_id INTEGER REFERENCES handle (ROWID) ON DELETE CASCADE, UNIQUE(chat_id, handle_id));
INSERT INTO chat_handle_join VALUES(2,2);
CREATE TABLE sync_deleted_messages (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, guid TEXT NOT NULL, recordID TEXT );
INSERT INTO sync_deleted_messages VALUES(1,'91ED3477-EDA9-48BF-8E87-873B37D804A8','');
INSERT INTO sync_deleted_messages VALUES(2,'D06D2D50-7C12-4114-B849-1A1D2146D306',NULL);
INSERT INTO sync_deleted_messages VALUES(3,'1EE3DB69-8FD1-478F-A7A7-D0C3D8716133',NULL);
INSERT INTO sync_deleted_messages VALUES(4,'096B56BF-5A85-4194-A5CA-4A9195AE0183',NULL);
INSERT INTO sync_deleted_messages VALUES(5,'D4A09E09-A6FE-40D6-B79C-B68A878B0568','');
INSERT INTO sync_deleted_messages VALUES(6,'0C78643A-0A67-4022-A3F2-301A9496F2AD','');
CREATE TABLE message_processing_task (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, guid TEXT NOT NULL, task_flags INTEGER NOT NULL );
CREATE TABLE handle (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, id TEXT NOT NULL, country TEXT, service TEXT NOT NULL, uncanonicalized_id TEXT, person_centric_id TEXT, UNIQUE (id, service) );
INSERT INTO handle VALUES(2,'blue@poggers.university','us','iMessage',NULL,NULL);
CREATE TABLE sync_deleted_chats (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, guid TEXT NOT NULL, recordID TEXT,timestamp INTEGER);
CREATE TABLE message_attachment_join (message_id INTEGER REFERENCES message (ROWID) ON DELETE CASCADE, attachment_id INTEGER REFERENCES attachment (ROWID) ON DELETE CASCADE, UNIQUE(message_id, attachment_id));
CREATE TABLE sync_deleted_attachments (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, guid TEXT NOT NULL, recordID TEXT );
INSERT INTO sync_deleted_attachments VALUES(1,'F0DA17FE-0A7B-4B8D-BAA0-0CB898315AA4',NULL);
CREATE TABLE kvtable (ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, key TEXT UNIQUE NOT NULL, value BLOB NOT NULL);
CREATE TABLE chat_message_join (chat_id INTEGER REFERENCES chat (ROWID) ON DELETE CASCADE, message_id INTEGER REFERENCES message (ROWID) ON DELETE CASCADE, message_date INTEGER DEFAULT 0, PRIMARY KEY (chat_id, message_id));
INSERT INTO chat_message_join VALUES(2,7,648927160045514368);
INSERT INTO chat_message_join VALUES(2,8,648927174089999872);
-- snip --
```

Alright, that's a lot of data to take in! Let's find out what tables are created and prepare our filters from there.

```sql
sqlite> .tables
_SqliteDatabaseProperties  kvtable
attachment                 message
chat                       message_attachment_join
chat_handle_join           message_processing_task
chat_message_join          sync_deleted_attachments
deleted_messages           sync_deleted_chats
handle                     sync_deleted_messages
```

The table "message" looks interesting. Let's have a look at that.

```sql
sqlite> .dump message
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE message (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, guid TEXT UNIQUE NOT NULL, text TEXT, replace INTEGER DEFAULT 0, service_center TEXT, handle_id INTEGER DEFAULT 0, subject TEXT, country TEXT, attributedBody BLOB, version INTEGER DEFAULT 0, type INTEGER DEFAULT 0, service TEXT, account TEXT, account_guid TEXT, error INTEGER DEFAULT 0, date INTEGER, date_read INTEGER, date_delivered INTEGER, is_delivered INTEGER DEFAULT 0, is_finished INTEGER DEFAULT 0, is_emote INTEGER DEFAULT 0, is_from_me INTEGER DEFAULT 0, is_empty INTEGER DEFAULT 0, is_delayed
INTEGER DEFAULT 0, is_auto_reply INTEGER DEFAULT 0, is_prepared INTEGER DEFAULT 0, is_read INTEGER DEFAULT 0, is_system_message INTEGER DEFAULT 0, is_sent INTEGER DEFAULT 0, has_dd_results
INTEGER DEFAULT 0, is_service_message INTEGER DEFAULT 0, is_forward INTEGER DEFAULT 0, was_downgraded INTEGER DEFAULT 0, is_archive INTEGER DEFAULT 0, cache_has_attachments INTEGER DEFAULT
0, cache_roomnames TEXT, was_data_detected INTEGER DEFAULT 0, was_deduplicated INTEGER DEFAULT 0, is_audio_message INTEGER DEFAULT 0, is_played INTEGER DEFAULT 0, date_played INTEGER, item_type INTEGER DEFAULT 0, other_handle INTEGER DEFAULT 0, group_title TEXT, group_action_type INTEGER DEFAULT 0, share_status INTEGER DEFAULT 0, share_direction INTEGER DEFAULT 0, is_expirable INTEGER DEFAULT 0, expire_state INTEGER DEFAULT 0, message_action_type INTEGER DEFAULT 0, message_source INTEGER DEFAULT 0, associated_message_guid TEXT, associated_message_type INTEGER DEFAULT 0, balloon_bundle_id TEXT, payload_data BLOB, expressive_send_style_id TEXT, associated_message_range_location INTEGER DEFAULT 0, associated_message_range_length INTEGER DEFAULT 0, time_expressive_send_played INTEGER, message_summary_info BLOB, ck_sync_state INTEGER DEFAULT 0, ck_record_id TEXT, ck_record_change_tag TEXT, destination_caller_id TEXT, sr_ck_sync_state INTEGER DEFAULT 0, sr_ck_record_id TEXT, sr_ck_record_change_tag TEXT, is_corrupt INTEGER DEFAULT 0, reply_to_guid TEXT, sort_id INTEGER, is_spam INTEGER DEFAULT 0, has_unseen_mention INTEGER DEFAULT 0, thread_originator_guid TEXT, thread_originator_part TEXT);
INSERT INTO message VALUES(7,'336CCB7F-3CB8-477A-AEED-8A4418EE7FFF','Hey what’s your Discord tag',0,NULL,2,NULL,NULL,X'040b73747265616d747970656481e803840140848484124e5341747472696275746564537472696e67008484084e534f626a656374008592848484084e53537472696e67019484012b1d4865792077686174e280997320796f757220446973636f7264207461678684026949011b928484840c4e5344696374696f6e617279009484016901928496961d5f5f6b494d4d657373616765506172744174747269627574654e616d658692848484084e534e756d626572008484074e5356616c7565009484012a84999900868686',10,0,'iMessage','E:red@poggers.university','73890C71-600D-4961-B1A7-687F2FAD3566',0,648927160045514368,648927163675579008,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,NULL,1,0,0,0,0,0,0,NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL,0,0,0,X'62706c6973743030d20102030453616d6353757374100009080d1115170000000000000101000000000000000500000000000000000000000000000018',0,NULL,NULL,'red@poggers.university',0,NULL,NULL,0,NULL,0,0,0,NULL,NULL);
INSERT INTO message VALUES(8,'0D123DA5-AB98-49EF-821A-5B9BC672E461','RedAmogus#8715',0,NULL,2,NULL,NULL,X'040b73747265616d747970656481e803840140848484194e534d757461626c6541747472696275746564537472696e67008484124e5341747472696275746564537472696e67008484084e534f626a6563740085928484840f4e534d757461626c65537472696e67018484084e53537472696e67019584012b0e526564416d6f67757323383731358684026949010e928484840c4e5344696374696f6e617279009584016901928498981d5f5f6b494d4d657373616765506172744174747269627574654e616d658692848484084e534e756d626572008484074e5356616c7565009584012a849b9b00868686',10,0,'iMessage','E:red@poggers.university','73890C71-600D-4961-B1A7-687F2FAD3566',0,648927174089999872,648927174257075840,648927174238451968,1,1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,NULL,1,0,0,0,0,0,0,NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL,0,0,0,X'62706c6973743030d101025375737409080b0f0000000000000101000000000000000300000000000000000000000000000010',0,'','','red@poggers.university',0,'','',0,'336CCB7F-3CB8-477A-AEED-8A4418EE7FFF',0,0,0,NULL,NULL);
INSERT INTO message VALUES(9,'8F42373C-2567-4CCE-8D2A-6EBB95E5FD1D','Ok I sent you a friend request',0,NULL,2,NULL,NULL,X'040b73747265616d747970656481e803840140848484124e5341747472696275746564537472696e67008484084e534f626a656374008592848484084e53537472696e67019484012b1e4f6b20492073656e7420796f75206120667269656e6420726571756573748684026949011e928484840c4e5344696374696f6e617279009484016901928496961d5f5f6b494d4d657373616765506172744174747269627574654e616d658692848484084e534e756d626572008484074e5356616c7565009484012a84999900868686',10,0,'iMessage','E:red@poggers.university','73890C71-600D-4961-B1A7-687F2FAD3566',0,648927183589449856,648927183862630016,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,NULL,1,0,0,0,0,0,0,NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL,0,0,0,X'62706c6973743030d20102030453616d6353757374100009080d1115170000000000000101000000000000000500000000000000000000000000000018',0,NULL,NULL,'red@poggers.university',0,NULL,NULL,0,'0D123DA5-AB98-49EF-821A-5B9BC672E461',0,0,0,NULL,NULL);
INSERT INTO message VALUES(10,'55C30F22-0A25-4391-BC0B-FD706018D307','We should communicate on there instead of iMessage',0,NULL,2,NULL,NULL,X'040b73747265616d747970656481e803840140848484124e5341747472696275746564537472696e67008484084e534f626a656374008592848484084e53537472696e67019484012b3257652073686f756c6420636f6d6d756e6963617465206f6e20746865726520696e7374656164206f6620694d65737361676586840269490132928484840c4e5344696374696f6e617279009484016901928496961d5f5f6b494d4d657373616765506172744174747269627574654e616d658692848484084e534e756d626572008484074e5356616c7565009484012a84999900868686',10,0,'iMessage','E:red@poggers.university','73890C71-600D-4961-B1A7-687F2FAD3566',0,648927208709548672,648927208949269120,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,NULL,1,0,0,0,0,0,0,NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL,0,0,0,X'62706c6973743030d20102030453616d6353757374100009080d1115170000000000000101000000000000000500000000000000000000000000000018',0,NULL,NULL,'red@poggers.university',0,NULL,NULL,0,'8F42373C-2567-4CCE-8D2A-6EBB95E5FD1D',0,0,0,NULL,NULL);
INSERT INTO message VALUES(11,'A5BE983C-196B-48DC-B412-CE69A8B115FE','🤢',0,NULL,2,NULL,NULL,X'040b73747265616d747970656481e803840140848484124e5341747472696275746564537472696e67008484084e534f626a656374008592848484084e53537472696e67019484012b04f09fa4a286840269490102928484840c4e5344696374696f6e617279009484016901928496961d5f5f6b494d4d657373616765506172744174747269627574654e616d658692848484084e534e756d626572008484074e5356616c7565009484012a84999900868686',10,0,'iMessage','E:red@poggers.university','73890C71-600D-4961-B1A7-687F2FAD3566',0,648927219266664448,648927219586212096,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,NULL,1,0,0,0,0,0,0,NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL,0,0,0,X'62706c6973743030d20102030453616d6353757374100009080d1115170000000000000101000000000000000500000000000000000000000000000018',0,NULL,NULL,'red@poggers.university',0,NULL,NULL,0,'55C30F22-0A25-4391-BC0B-FD706018D307',0,0,0,NULL,NULL);
COMMIT;
```

That's still a lot to take in! It may be valuable to understand how this table is constructed:

```sql
CREATE TABLE message (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, guid TEXT UNIQUE NOT NULL, text TEXT, replace INTEGER DEFAULT 0, service_center TEXT, handle_id INTEGER DEFAULT 0, subject TEXT, country TEXT, attributedBody BLOB, version INTEGER DEFAULT 0, type INTEGER DEFAULT 0, service TEXT, account TEXT, account_guid TEXT, error INTEGER DEFAULT 0, date INTEGER, date_read INTEGER, date_delivered INTEGER, is_delivered INTEGER DEFAULT 0, is_finished INTEGER DEFAULT 0, is_emote INTEGER DEFAULT 0, is_from_me INTEGER DEFAULT 0, is_empty INTEGER DEFAULT 0, is_delayed
```

Based on this, we can prepare a SQL query to only return data from the column "text" in the table "message."

```sql
sqlite> SELECT text FROM message;
Hey what’s your Discord tag
RedAmogus#8715
Ok I sent you a friend request
We should communicate on there instead of iMessage
🤢
```

Just as a quick aside, I found this to be really funny while I was doing the challenge:

```sql
sqlite> SELECT account FROM message;
E:red@poggers.university
E:red@poggers.university
E:red@poggers.university
E:red@poggers.university
E:red@poggers.university
```

[poggers.university](https://poggers.university/) just redirects to [illinois.edu](https://illinois.edu/). That gave me a good laugh.

Back to the challenge, it looks like our next target is Discord. If you recall from earlier in **forensics/Tablet 1**, we found that Discord was one of the apps on the tablet:

```sh
[skat@anubis:~/.../Containers] $ find . -name "com.*" | awk -F '/' '{print $NF}' | sort | uniq -u | grep -v "com.apple"
com.crashlytics
com.crashlytics.data
com.firebase.FIRInstallations.plist
com.google.gmp.measurement.monitor.plist
com.google.gmp.measurement.plist
com.hackemist.SDImageCache
com.hammerandchisel.discord - {DEFAULT GROUP}
com.hammerandchisel.discord.plist
com.hammerandchisel.discord.savedState
com.innersloth.amongus - {DEFAULT GROUP}
com.innersloth.amongus.plist
com.innersloth.amongus.savedState
com.itimeteo.webssh - {DEFAULT GROUP}
com.itimeteo.webssh.plist
com.itimeteo.webssh.savedState
com.plausiblelabs.crashreporter.data
```

Let's go ahead and see what kind of data we can recover from the saved Discord application data on this tablet using the same method we used earlier for the SSH client:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ find . -name "com.hammerandchisel.discord - {DEFAULT GROUP}"
./mobile/Containers/Data/Application/0CE5D539-F72A-4C22-BADF-A02CE5A50D2E/Library/SplashBoard/Snapshots/com.hammerandchisel.discord - {DEFAULT GROUP}
[skat@anubis:~/work/UIUCTF/private/var] $ cd ./mobile/Containers/Data/Application/0CE5D539-F72A-4C22-BADF-A02CE5A50D2E/
[skat@anubis:~/.../0CE5D539-F72A-4C22-BADF-A02CE5A50D2E] $ tree
.
├── Documents
│   ├── mmkv
│   │   ├── mmkv.default
│   │   └── mmkv.default.crc
│   └── RCTAsyncLocalStorage_V1
├── Library
│   ├── Application Support
│   │   ├── Adjust
│   │   │   ├── AdjustIoActivityState
│   │   │   ├── AdjustIoAttribution
│   │   │   └── AdjustIoPackageQueue
│   │   ├── com.crashlytics
│   │   │   └── CLSUserDefaults.plist
│   │   └── Google
│   │       ├── FIRApp
│   │       │   ├── FIREBASE_DIAGNOSTICS_HEARTBEAT_DATE
│   │       │   └── HEARTBEAT_INFO_STORAGE
│   │       └── Measurement
│   │           ├── google-app-measurement.sql
│   │           └── google_experimentation_database.sql
│   ├── Caches
│   │   ├── assets
│   │   │   ├── components_ios
│   │   │   │   └── add_friend
│   │   │   │       └── images
│   │   │   │           ├── nearby_scan@2x.png
│   │   │   │           └── nearby_scan@3x.png
│   │   │   ├── data
│   │   │   │   ├── country-codes.json
│   │   │   │   ├── emoji-shortcuts.json
│   │   │   │   └── emojis.json
│   │   │   ├── i18n
│   │   │   │   ├── languages.json
│   │   │   │   └── messages
│   │   │   │       ├── bg.json
│   │   │   │       ├── cs.json
│   │   │   │       ├── da.json
│   │   │   │       ├── de.json
-- snip --
```

1,843 lines of output, and we don't really care about most of these files! Just like before when we found what we were looking for in the application's database file, let's apply the same idea here and see if we can find what we're looking for in the Discord app's database file(s):

```sh
[skat@anubis:~/.../0CE5D539-F72A-4C22-BADF-A02CE5A50D2E] $ find . -name "*.db"
./Library/Caches/com.hammerandchisel.discord/Cache.db
./Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db
```

`Cache.db` probably has some really interesting information valuable to us! Perhaps we can find cached messages or contacts. Let's load up the database and dig around:

```sh
[skat@anubis:~/.../0CE5D539-F72A-4C22-BADF-A02CE5A50D2E] $ cd ./Library/Caches/com.hammerandchisel.discord/
[skat@anubis:~/.../com.hammerandchisel.discord] $ sqlite3 Cache.db
```

```sql
SQLite version 3.36.0 2021-06-18 18:36:39
Enter ".help" for usage hints.
sqlite> .dump
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,     version INTEGER, hash_value INTEGER, storage_policy INTEGER, request_key TEXT UNIQUE,   time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP, partition TEXT);
INSERT INTO cfurl_cache_response VALUES(1,0,1139453470654270506,0,'https://discord.com/ios/83.0/manifest.json','2021-07-25 18:56:41',NULL);
INSERT INTO cfurl_cache_response VALUES(2,0,-1441044142,0,'https://discord.com/api/v9/gateway','2021-07-25 18:56:42',NULL);
INSERT INTO cfurl_cache_response VALUES(3,0,2017693604,0,'https://discord.com/api/v9/channels/868908952434384926/messages?limit=25','2021-07-25 18:56:43',NULL);
INSERT INTO cfurl_cache_response VALUES(4,0,-1637691448,0,'https://latency.discord.media/rtc','2021-07-25 18:57:06',NULL);
CREATE TABLE cfurl_cache_blob_data(entry_ID INTEGER PRIMARY KEY, response_object BLOB, request_object BLOB,               proto_props BLOB, user_info BLOB);
INSERT INTO cfurl_cache_blob_data VALUES(1,X'62706c6973743030d2010203045756657273696f6e5541727261791001a7050a0b0c0d3839d2060708095f10105f434655524c537472696e67547970655c5f434655524c537472696e67100f5f102a68747470733a2f2f646973636f72642e636f6d2f696f732f38332e302f6d616e69666573742e6a736f6e2341c356f5b49c4a27100010c8df10150e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f30313233343536375f1010436f6e74656e742d456e636f64696e675a782d6275696c642d69645663662d726179565365727665725d43616368652d436f6e74726f6c5f10195374726963742d5472616e73706f72742d5365637572697479585f5f686861615f5f5f10127065726d697373696f6e732d706f6c69637957416c742d537663597265706f72742d746f5f1010782d7873732d70726f74656374696f6e544461746554566172795f100f782d6672616d652d6f7074696f6e73536e656c596578706563742d63745c436f6e74656e742d5479706554457461675f100f63662d63616368652d7374617475735d4c6173742d4d6f6469666965645f1016782d636f6e74656e742d747970652d6f7074696f6e7354677a697057616534663662645f1014363734373963313133653630326137652d4f52445a636c6f7564666c617265586e6f2d63616368655f102c6d61782d6167653d33313533363030303b20696e636c756465537562446f6d61696e733b207072656c6f61645f11069c0d0a0d0a596e427361584e304d4444664542514241674d454251594843416b4b4377774e446738514552495446425558475273644879456a4a5363704b7930764d544d314e7a6b3758784151513239756447567564433146626d4e765a476c755a3170344c574a316157786b4c576c6b58557868633351745457396b61575a705a57525755325679646d567958554e685932686c4c554e76626e52796232786645426c5464484a705933517456484a68626e4e7762334a304c564e6c5933567961585235587841536347567962576c7a63326c76626e4d746347397361574e355630467364433154646d4e5a636d567762334a304c585276587841516543313463334d7463484a766447566a64476c76626c52455958526c56465a68636e6c66454139344c575a795957316c4c57397764476c76626e4e54626d5673575756346347566a6443316a64467844623235305a5735304c56523563475655525852685a31385144324e6d4c574e685932686c4c584e305958523163313851466e67745932397564475675644331306558426c4c57397764476c76626e4e5759325974636d46356f525a555a337070634b45595632466c4e475932596d5368476c38514856646c5a4377674d6a4567536e5673494449774d6a45674d5467364d5451364d544967523031556f527861593278766457526d624746795a614565574735764c574e685932686c6f53426645437874595867745957646c50544d784e544d324d4441774f794270626d4e736457526c553356695247397459576c75637a736763484a6c624739685a4b456958784153615735305a584a6c633351745932396f62334a30505367706f5352664546746f4d7930794e7a30694f6a51304d79493749473168505467324e4441774c43426f4d7930794f4430694f6a51304d79493749473168505467324e4441774c43426f4d7930794f5430694f6a51304d79493749473168505467324e4441774c43426f4d7a30694f6a51304d79493749473168505467324e4441776f535a66454f7437496d56755a48427661573530637949365733736964584a73496a6f696148523063484d36584339634c324575626d56734c6d4e736233566b5a6d7868636d557559323974584339795a584276636e52634c33597a50334d394f58566a52336c5661335a776348593261474e786258457862334e764a544a475448676c4d6b5a46636e685853323552556d78305a444d786358593554555a7455327733546c4931546e46745532706d534452764e6a6b6c4d6b4a6e56336c7653585a69596e4e685232566c51556f784e577333576b784552474e53576b566963304e3264335a524d4855784d554532636d704a613064505932684f544851306145394864466853626c553165534a39585377695a334a76645841694f694a6a5a6931755a5777694c434a74595868665957646c496a6f324d4451344d4442396f5368644d5473676257396b5a5431696247396a6136457158784164553356754c4341794e53424b645777674d6a41794d5341784f446f314e6a6f304d534248545653684c4638514430466a5932567764433146626d4e765a476c755a36457556455246546c6d684d4638514a337369636d567762334a3058335276496a6f6959325974626d567349697769625746345832466e5a5349364e6a41304f4441776661457958784258625746344c57466e5a5430324d4451344d44417349484a6c6347397964433131636d6b39496d68306448427a4f693876636d567762334a304c5856796153356a624739315a475a7359584a6c4c6d4e766253396a5a473474593264704c324a6c59574e766269396c6548426c59335174593351696f545266454242686348427361574e6864476c7662693971633239756f545a66454352584c7949774e3249314d6d466b4d4463305a446c6c4e5467314f4452694f5759784e6a4d304d4451354f575a6a5a434b684f464e49535653684f6c647562334e7561575a6d6f547866454251324e7a51334f574d784d544e6c4e6a41795954646c4c5539535241414941444d4152674252414638415a674230414a414170514374414c634179674450414e5141356744714150514241514547415267424d51453441546f425077464241556b4253774672415730426541463641594d4268514730416259427977484e416973434c514d62417830444b774d744130304454774e6841324d4461414e71413551446c675077412f494542515148424334454d4151304244594550675241414141414141414141674541414141414141414150514141414141414141414141414141414141414246633d5f1012696e7465726573742d636f686f72743d28295f105b68332d32373d223a343433223b206d613d38363430302c2068332d32383d223a343433223b206d613d38363430302c2068332d32393d223a343433223b206d613d38363430302c2068333d223a343433223b206d613d38363430305f10eb7b22656e64706f696e7473223a5b7b2275726c223a2268747470733a5c2f5c2f612e6e656c2e636c6f7564666c6172652e636f6d5c2f7265706f72745c2f76333f733d3975634779556b76707076366863716d71316f736f2532464c78253246457278574b6e51526c746433317176394d466d536c374e52354e716d536a6648346f36392532426757796f497662627361476565414a31356b375a4c444463525a4562734376777651307531314136726a496b474f63684e4c7434684f477458526e553579227d5d2c2267726f7570223a2263662d6e656c222c226d61785f616765223a3630343830307d5d313b206d6f64653d626c6f636b5f101d53756e2c203235204a756c20323032312031383a35363a343120474d545f100f4163636570742d456e636f64696e675444454e595f10277b227265706f72745f746f223a2263662d6e656c222c226d61785f616765223a3630343830307d5f10576d61782d6167653d3630343830302c207265706f72742d7572693d2268747470733a2f2f7265706f72742d7572692e636c6f7564666c6172652e636f6d2f63646e2d6367692f626561636f6e2f6578706563742d6374225f10106170706c69636174696f6e2f6a736f6e5f1024572f22303762353261643037346439653538353834623966313633343034393966636422534849545f101d5765642c203231204a756c20323032312031383a31343a313220474d54576e6f736e6966661200023b6e5f10106170706c69636174696f6e2f6a736f6e0008000d0015001b001d0025002a003d004a004c007900820084008600b300c600d100d800df00ed010901120127012f0139014c015101560168016c017601830188019a01a801c101c601ce01e501f001f9022808c808dd093b0a290a370a570a690a6e0a980af20b050b2c0b300b500b580b5d0000000000000201000000000000003a00000000000000000000000000000b70',X'62706c6973743030d2010203045756657273696f6e5541727261791009af101605060b0c0d0e0f0d0d0e0512131312140d1516170d0d08d20708090a5f10105f434655524c537472696e67547970655c5f434655524c537472696e67100f5f102a68747470733a2f2f646973636f72642e636f6d2f696f732f38332e302f6d616e69666573742e6a736f6e23404e00000000000010015f101f5f5f434655524c526571756573744e756c6c546f6b656e537472696e675f5f0910840908100023000000000000000013ffffffffffffffff100253474554d618191a1b1c1d1e1f202122235a557365722d4167656e745f100f4163636570742d4c616e6775616765564163636570745d49662d4e6f6e652d4d617463685f100f4163636570742d456e636f64696e67585f5f68686
-- snip --
```

There's a lot of data, so let's pipe everything to `grep` and find out how the tables are created:

```sh
[skat@anubis:~/.../com.hammerandchisel.discord] $ sqlite3 Cache.db ".dump" | grep "CREATE TABLE"
```

```sql
CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,     version INTEGER, hash_value INTEGER, storage_policy INTEGER, request_key TEXT UNIQUE,   time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP, partition TEXT);
CREATE TABLE cfurl_cache_blob_data(entry_ID INTEGER PRIMARY KEY, response_object BLOB, request_object BLOB,               proto_props BLOB, user_info BLOB);
CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER PRIMARY KEY, isDataOnFS INTEGER, receiver_data BLOB);
```

Given that most of what is presumably our mother lode data are data blobs, let's dump those blobs and see what they say. It takes a bit of trial and error until we find what we're looking for in the `receiver_data` blob column of the table `cfurl_cache_receiver_data`:

```sh
[skat@anubis:~/.../com.hammerandchisel.discord] $ sqlite3 Cache.db "SELECT receiver_data FROM cfurl_cache_receiver_data"
7EE02011-9C66-45A1-BFE4-CB18F2251F24
{"url": "wss://gateway.discord.gg"}
[{"id": "868914084370866187", "type": 0, "content": "", "channel_id": "868908952434384926", "author": {"id": "868302522304053248", "username": "RedAmogus", "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd", "discriminator": "8715", "public_flags": 0}, "attachments": [{"id": "868914084639293490", "filename": "image0.jpg", "size": 13859, "url": "https://cdn.discordapp.com/attachments/868908952434384926/868914084639293490/image0.jpg", "proxy_url": "https://media.discordapp.net/attachments/868908952434384926/868914084639293490/image0.jpg", "width": 421, "height": 421, "content_type": "image/jpeg"}], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:54:21.357000+00:00",
"edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913936542597140", "type": 0, "content": "Ok", "channel_id": "868908952434384926", "author": {"id": "868302522304053248",
"username": "RedAmogus", "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd", "discriminator": "8715", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:53:46.112000+00:00", "edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913804002607114", "type": 0, "content": "The password is ||su5Syb@k4||", "channel_id": "868908952434384926", "author": {"id": "868907394569207858", "username": "BlueAmogus", "avatar": "92f083abd028e406866677d86f4ca3d4", "discriminator": "8346", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:53:14.512000+00:00", "edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913676176994324", "type": 0, "content": "I sent you an encrypted note with all the details", "channel_id": "868908952434384926", "author": {"id": "868907394569207858", "username": "BlueAmogus", "avatar": "92f083abd028e406866677d86f4ca3d4", "discriminator": "8346", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:52:44.036000+00:00", "edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913627615363103", "type": 0, "content": "I'll deal with them, you just make sure this next sabotage goes to plan", "channel_id": "868908952434384926", "author": {"id": "868907394569207858", "username": "BlueAmogus", "avatar": "92f083abd028e406866677d86f4ca3d4", "discriminator": "8346", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:52:32.458000+00:00", "edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913576629403659", "type": 0, "content": "White is onto me\u2026 they kept calling me out last meeting", "channel_id": "868908952434384926", "author": {"id": "868302522304053248", "username": "RedAmogus", "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd", "discriminator": "8715", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:52:20.302000+00:00", "edited_timestamp": null, "flags": 0, "components": []}, {"id": "868913513463181332", "type": 0, "content": "Yo", "channel_id": "868908952434384926", "author": {"id": "868302522304053248", "username": "RedAmogus", "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd", "discriminator": "8715", "public_flags": 0}, "attachments": [], "embeds": [], "mentions": [], "mention_roles": [], "pinned": false, "mention_everyone": false, "tts": false, "timestamp": "2021-07-25T17:52:05.242000+00:00", "edited_timestamp": null, "flags": 0, "components": []}]
[{"region":"us-central","ips":["138.128.141.109","138.128.143.75","138.128.142.25","138.128.143.90","138.128.143.9"]},{"region":"us-east","ips":["162.244.55.137","35.212.111.96","35.212.103.235","35.212.77.192","35.212.111.72"]},{"region":"atlanta","ips":["31.204.134.61","31.204.134.50","31.204.133.74","31.204.134.36","31.204.133.27"]},{"region":"newark","ips":["109.200.210.38","109.200.210.45","109.200.210.27","109.200.210.51","109.200.210.42"]},{"region":"us-south","ips":["138.128.139.7","138.128.137.12","138.128.139.16","138.128.137.190","138.128.138.244"]}]
```

Great, some data! Let's toss this into a code prettifier for easier reading:

```json
[
  {
    "id": "868914084370866187",
    "type": 0,
    "content": "",
    "channel_id": "868908952434384926",
    "author": {
      "id": "868302522304053248",
      "username": "RedAmogus",
      "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd",
      "discriminator": "8715",
      "public_flags": 0
    },
    "attachments": [
      {
        "id": "868914084639293490",
        "filename": "image0.jpg",
        "size": 13859,
        "url": "https://cdn.discordapp.com/attachments/868908952434384926/868914084639293490/image0.jpg",
        "proxy_url": "https://media.discordapp.net/attachments/868908952434384926/868914084639293490/image0.jpg",
        "width": 421,
        "height": 421,
        "content_type": "image/jpeg"
      }
    ],
    "embeds": [],
    "mentions": [],
    "mention_roles": [],
    "pinned": false,
    "mention_everyone": false,
    "tts": false,
    "timestamp": "2021-07-25T17:54:21.357000+00:00",
    "edited_timestamp": null,
    "flags": 0,
    "components": []
  },
  {
    "id": "868913936542597140",
    "type": 0,
    "content": "Ok",
    "channel_id": "868908952434384926",
    "author": {
      "id": "868302522304053248",
      "username": "RedAmogus",
      "avatar": "f15b13e77a7fe5ef2d4b4d13be65d1dd",
      "discriminator": "8715",
      "public_flags": 0
    },
    "attachments": [],
    "embeds": [],
    "mentions": [],
    "mention_roles": [],
    "pinned": false,
    "mention_everyone": false,
    "tts": false,
    "timestamp": "2021-07-25T17:53:46.112000+00:00",
    "edited_timestamp": null,
    "flags": 0,
    "components": []
  },
-- snip --
```

Based on this little snippet, it looks like messages are stored in a field called "content." We can throw the prettified code into a file and then `grep` it to quickly give us only the messages themselves without all the other data that comes along with them:

```sh
[skat@anubis:~/dl] $ grep "\"content\":" codebeautify.json
    "content": "",
    "content": "Ok",
    "content": "The password is ||su5Syb@k4||",
    "content": "I sent you an encrypted note with all the details",
    "content": "I'll deal with them, you just make sure this next sabotage goes to plan",
    "content": "White is onto me… they kept calling me out last meeting",
    "content": "Yo",
```

Just like that, we have the messages from Red's conversation with... with whom? Let's try to get the usernames as well so that we can better understand the situation:

```sh
[skat@anubis:~/dl] $ grep "\"content\":\|\"username\":" codebeautify.json
    "content": "",
      "username": "RedAmogus",
    "content": "Ok",
      "username": "RedAmogus",
    "content": "The password is ||su5Syb@k4||",
      "username": "BlueAmogus",
    "content": "I sent you an encrypted note with all the details",
      "username": "BlueAmogus",
    "content": "I'll deal with them, you just make sure this next sabotage goes to plan",
      "username": "BlueAmogus",
    "content": "White is onto me… they kept calling me out last meeting",
      "username": "RedAmogus",
    "content": "Yo",
      "username": "RedAmogus",
```

It looks like Red is in contact with Blue, and Blue sent Red a note encrypted with the password `su5Syb@k4`. Given that Red is running an Apple system, it would be logical to entertain the hunch that this must be an Apple note. Let's try finding where these files are located on the iPad:

```sh
[skat@anubis:~/work/UIUCTF/private/var] $ find . -name "Note"
[skat@anubis:~/work/UIUCTF/private/var] $ find . -name "Note*"
./mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NotesIndexerState-Modern
./mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NotesIndexerState-Legacy
./mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NoteStore.sqlite-shm
./mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NoteStore.sqlite-wal
./mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NoteStore.sqlite
./mobile/Library/Assistant/CustomVocabulary/com.apple.reminders/0000000000000000000000000000000000000000/NotebookItemTitleType
./mobile/Library/Notes
```

Great, more databases! We should be familiar with the process by now, but there's an added catch: Blue mentioned that the note is encrypted. If we try accessing the database as it currently is, then it's pretty useless to us. We need some kind of parser, such as [apple_cloud_notes_parser](https://github.com/threeplanetssoftware/apple_cloud_notes_parser), in order to decrypt the note using the `notes.sqlite` file:

```sh
[skat@anubis:~/dl/apple_cloud_notes_parser] $ echo "su5Syb@k4" > password.txt
[skat@anubis:~/dl/apple_cloud_notes_parser] $ ruby notes_cloud_ripper.rb -f ~/work/UIUCTF/private/var/mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NoteStore.sqlite -w password.txt

Starting Apple Notes Parser at Wed Aug  4 13:27:05 2021
Storing the results in ./output/2021_08_04-13_27_05

Created a new AppleBackup from single file: /home/skat/work/UIUCTF/private/var/mobile/Containers/Shared/AppGroup/4DCEB2C7-5420-4446-9111-4091A929B4AC/NoteStore.sqlite
Guessed Notes Version: 14
Added 1 passwords to the AppleDecrypter from password.txt
Updated AppleNoteStore object with 1 AppleNotes in 2 folders belonging to 1 accounts.
Adding the ZICNOTEDATA.ZPLAINTEXT and ZICNOTEDATA.ZDECOMPRESSEDDATA columns, this takes a few seconds

Successfully finished at Wed Aug  4 13:27:05 2021
```

Great, it looks like we were able to successfully decrypt the note! Let's check out the data:

```sh
[skat@anubis:~/dl/apple_cloud_notes_parser] $ cd output/2021_08_04-13_27_05/
[skat@anubis:~/dl/apple_cloud_notes_parser/output/2021_08_04-13_27_05] $ ls
csv  html  debug_log.txt  NoteStore.sqlite
[skat@anubis:~/dl/apple_cloud_notes_parser/output/2021_08_04-13_27_05] $ tree
.
├── csv
│   ├── note_store_accounts_1.csv
│   ├── note_store_cloudkit_participants_1.csv
│   ├── note_store_embedded_objects_1.csv
│   ├── note_store_folders_1.csv
│   └── note_store_notes_1.csv
├── debug_log.txt
├── html
│   └── all_notes_1.html
├── NoteStore.sqlite
└── output.dat

2 directories, 9 files
```

It looks like `NoteStore.sqlite` is the original encrypted note store, and `csv` and `html` are directories containing the decrypted output. Let's have a look at `all_notes_1.html` by opening it up in a web browser:

![](/uploads/2021-08-07/all_notes_1.png)

We've successfully uncovered what Red and Blue are plotting and in the process, we captured the flag!

<h3 id="debriefing-2">Debriefing</h3>

We were initially given new information and told that Red had been communicating with another impostor; our objective was to find out who Red and this other impostor were plotting. Looking through Red's SMS text messages on the iPad device, we learned that they agreed with this new party to communicate via Discord. Looking through the cached application data from the Discord app present on Red's device, we discover that the other impostor is Blue and they sent Red an encrypted note with the password given in the Discord chat. Upon locating and decrypting the encrypted note from the device's note store, we uncover what Red and Blue were plotting.

This was great and absolutely something that I can see mirroring a real-life scenario! I can say for a fact that I've asked people before to switch from SMS to another service such as Discord since it's easier for me to type from a keyboard. I can also say for a fact that I've discovered a mother lode of data in saved application data and cached application data, and that's something you can expect from real-life scenarios as well! By understanding our situation well and by orienting ourselves at every step, we were able to much more precisely and intently execute our investigation.

## Conclusion

These were a great set of challenges and definitely some of the best forensics challenges I've ever done at a CTF event! At no point did I feel that these challenges were guessy, and I was appreciative at every step of the way of how closely this challenge could mirror a real-life investigation -- something that many CTFs shy away from. For anyone looking to get an idea of what a digital forensics specialist may encounter in their investigations and operations, this challenge gives a great idea!

That's all I have to offer for these two challenges. However, I do have two additional writeups from this CTF authored available immediately if you'd like to read them now. These were a lot of fun to author and took me nearly a week of writing, editing, proofreading, and revising until I finally decided to publish them.
