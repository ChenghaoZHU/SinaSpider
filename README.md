# SinaSpider - A Distributed Spider System for Sina Weibo

## 1. Working Schema
This spider system is programmed by pure Python code and works as Master-Slave schema.

The master node does nothing for crawling, it's just responsible for task assignment and data storage; while the slave nodes mainly do the crawling job and commit the parsed data to the master node for persistence.

For one spider running on a slave node, everytime it fetches a batch of uid (Weibo user ID) as its crawling task from the master node. Then the spider starts to crawl the data, and there are four parts for one user, that's followee, follower, timeline and profile. It's noting that one spider use multiple Weibo accounts to do the crawling with the round-robin strategy. That's to say, when one account is working, the remain ones are in their rest, then the second account starts to work after a period and the previous one takes its rest. Things go like this. 

## 2. Environment Deployment

## 3. Get Started

## 4. FAQ


