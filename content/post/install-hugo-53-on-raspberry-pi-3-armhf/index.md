---
author: "Lee Doughty"
date: 2018-01-20
title: "Install Hugo 0.53 on Raspberry Pi 3 B+ armv71/armhf"
tags:
  - hugo
  - raspberry-pi
categories:
  - Nerd Stuff
---

**Short Summary:** This article will show you how you can install Hugo on a raspberry ARMv71/armhf) architecture -- which is what the more recent Raspberry Pi's are reporting at in modern OS's -- despite the fact Hugo's project doesn't publish the armhf package on their GitHub page.

<!--more-->

## Preparing the System
I'm going to assume you have Raspberry Pi 3b, or another raspberry pi that uses armv71/armhf architecture. I'm also assuming you use Raspbian, or another OS that can use debian packages.

## Install prerequisites
I only needed libsass1 on my system, but here are all the dependencies I could find for hugo:

```
sudo apt-get install libsass1 libc6 libgcc1 libstdc++6
```

If your distribution can't download that, you might be able to find a similar package you can install manually like we do in the next step.

## Download & Install Hugo
Grab the package directly from Debian:

```
wget http://ftp.us.debian.org/debian/pool/main/h/hugo/hugo_0.53-3_armhf.deb
sudo dpkg -i hugo_0.53-3_armhf.deb 
```

This should leave you with either a broken install, suggesting more packages to install, or a working Hugo install!

If you are missing more dependencies, you can try and run the following to resolve them:
```
sudo apt-get install -y (package given by an error message)
# Try to auto-resolve the issue
sudo apt install --fix-broken -y
```

## My use Case
Most people don't want a long story up front -- "Just get to the steps!" -- so here's my story: This website is built with Hugo, and I wanted to run the Hugo dev server and code IDE on my Pi. Hugo, unfortunately, does not publish an armhf package on their GitHub releases page, so I looked around for solutions. The first one I thought was to build it myself, but after a few minutes, I realized that will be annoying extra step.. So another quick search and I found Debian (which Raspbian is based on) _does_ make a Hugo package for armhf! Presto, problem solved, and article made to share!

Hope this helps someone!