---
author: "Lee Doughty"
date: 2019-08-20
title: "GitHub Webhook triggered Serverless AWS deploy of static Hugo website"
tags:
  - aws
categories:
  - aws-articles
---

**Summary**: This article will go over the basics to do an AWS Lambda deploy to AWS S3 + CloudFront of a Hugo static website after you merge to your master branch in GitHub. As an optional bonus step, you can add E-mail and other notifications when this happens. In theory this is applicable to other static website generators, but most of the article is not portable to other cloud vendors since the processor and target are both AWS.

<!--more-->

## Pre-requisites

This article assumes you have an AWS account, and are trying to automate building a website through a static site generator.

Notes:

* You will need significant AWS permissions to follow along.
* You will need a GitHub account (though in theory GitLab should also work)
* This is not always a completely free service, so you may be billed for the resulting product. My experience: This costs less than $0.05/month to run my website, but costs obviously vary with usage.

## Introduction

I saw an article on [Hacker News](https://news.ycombinator.com/) about serverless webpages, which was annoying to some readers because the deploy process was not serverless, only the resulting product was serverless. Since you can build Hugo and deploy from your local machine, why set up a CICD server to deploy your website? You're then still paying for a server!

That said, there can be advantages to offloading this. If you worked on a team, this kind of setup would allow multiple people to branch and merge, and any accepted and merged to master content would be auto-published to your destination.
