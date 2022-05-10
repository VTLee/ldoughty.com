---
author: "Lee Doughty"
date: 2022-05-09
title: "Exploring AWS Aurora Serverless v2 for cheap WordPress usage"
tags:
  - aws
  - serverless
categories:
  - aws-articles
---

**Summary**: I wanted to know if the new Aurora Serverless V2 could be used for a cheap wordpress instance, I was disappointed 

<!--more-->

## Goal

I've run a few small WordPress instances over the years on AWS. For the most part, I've not found a most cost-effective solution than LightSail, with a local DB, and scripts to export backups to something like S3. I was hoping that Aurora Serverless v2 would make a bearable cost DB, but I was disappointed... Details below...

## Background

[Aurora Serverless V2](https://aws.amazon.com/about-aws/whats-new/2022/04/amazon-aurora-serverless-v2/) was released in April. The pricing page for both MySQL and Postgres compatible Amazon Serverless v2 states on [their pricing page](https://aws.amazon.com/rds/aurora/pricing/) that: 

> In addition to gaining access to v2 features, most Aurora Serverless customers can lower costs by moving to v2 due to a lower starting capacity of 0.5 ACU (vs. 1 ACU in v1), smaller capacity increments of 0.5 ACU (vs. doubling in v1), and up to 15x faster scale down in capacity compared to Aurora Serverless v1. 

This is what initially got me interested in v2 of Serverless; at 0.5 ACU. The promise above was followed with:

> For example, consider a workload that needs 0.5 ACU of capacity and runs for only one hour every day. With Aurora Serverless v2, the database would start up with 0.5 ACU, run for one hour, and then shut down in under a minute. The compute cost for the workload on Aurora Serverless v2 is $0.06 in US East (Ohio) ($0.12/ACU-hour x 0.5 ACU x 1 hour). The same workload would start up with 1 ACU in Aurora Serverless v1, run for one hour, and shut down in another 15 minutes. Overall, for the same workload, the cost of compute in Aurora Serverless v1 is $0.075 ($0.06/ACU-hour x 1 ACU x 1.25 hour).

## The reality

The promised statements seems to hint that, if the DB is not in use, it might cost nothing? Not quite... You actually have to trigger the "Stop" mechanic of Serverless v2 yourself -- it's not automatic. If you do not, then 0.5 ACU 24x7 for the 720 hours that Amazon has as an average month would be $43.20/month at 0.5 ACU.

However, to actually get 0.5ACU's, you need to do _less than nothing_... I'm not kidding.

**At 0.5 ACUs, an empty DB is at 95+% usage**, with only the starting -- empty -- database, no logging, no connections, no public IP, nothing that _can_ access it. This causes the DB to scale up the DB to at least 1 ACU and doubles the minimum theoretical rate and makes the 0.5 ACU an "empty promise" -- it's not possible to stay at 0.5 ACU (unless you set .5 ACU as both the minimum and maximum -- disabling scaling) with an empty DB and no usage, so why even offer this?

What is the DB even doing to stay at 95+% CPU usage when there's a single database, no tables, and nothing going on? I'm assuming this is the equivalent of a t3.nano instance, and getting 10% of a single CPU thread, so it's really sitting at 10% on a throttled CPU... but still...

Anyways, this makes the minimum cost for a WordPress DB not $43.20 (before the usage costs), but $86.40...


## Use for Wordpress

I wanted to go further with this, but at $86 to play, I lost any motivation... It's cheaper to go with a t4g.medium RDS instance ($54/month), or Lightsail's DB ($15-60, depending on high-availability and how low a spec you need). Of course, if you're comfotable with it, you can also host the DB alongside your website -- but that puts even more on you to manage.