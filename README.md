# SinaSpider - A Distributed Spider System for Sina Weibo

## 1. Working Schema
This spider system is programmed by pure Python code and works as Master-Slave schema.

The master node does nothing for crawling, it's just responsible for task assignment and data storage; while the slave nodes mainly do the crawling job and commit the parsed data to the master node for persistence.

For one spider running on a slave node, everytime it fetches a batch of uid (Weibo user ID) as its crawling task from the master node. Then the spider starts to crawl the data, and there are four parts for one user's Weibo data, that's followee, follower, timeline and profile. It's noting that one spider use multiple Weibo accounts to do the crawling with the round-robin strategy. That's to say, when one account is working, the remain ones are in their rest, then the second account starts to work after a period and the previous one takes its rest. Things go like this. 

## 2. Environment Deployment
### 2.1 Get the Source Code
	git clone https://github.com/ChenghaoZHU/SinaSpider.git
### 2.2 Install Relevant Dependencies
1. rsa
2. PIL
3. sqlalchemy
4. pymysql
5. caca-utils (Only necessary for Linux)

If you have installed anaconda and use Red Hat Linux, following commands may be helpful:
	
	conda install -c https://conda.anaconda.org/jiangxiluning rsa
	conda install PIL
	conda install sqlalchemy
	conda install pymysql

	sudo yum install caca-utils 
	
## 3. Get Started
Before you run the spider with:
	
	python CompleteCrawl.py

You should edit the **Config.py** file first.
All the parameters in this file are listed as follows:

|Variable|Description|
|:---:|:---:|
|LOG_FILE|Log file path|
|SLEEP_BETWEEN_2FPAGES|Program sleeping time after reading one relationship page|
|SLEEP_BETWEEN_TIMELINE_PAGES|Program sleeping time between two timeline pages' reading|
|SLEEP_WHEN_EXCEPTION|Program sleeping time when encountering exceptions|
|ACCOUNT_CHANGE_TIME|Single account working time span|
|TABLES|Mapping relationships from program variables to database tables|
|DB_USER|Database user name|
|DB_PASSWD|Database user password|
|DB_HOST|IP address of database|
|DB_DATABASE|Database name|
|DB_CHARSET|Database character set|
|ACCOUNT_NUM|Account number one spider uses|
|TASK_NUM|Amount one batch of uid contains|
|OS|0 is for Windows, and 1 is for Linux|

Usually, you could just only edit **DB_USER**, **DB_PASSWD**, **DB_HOST** and **OS** to start a spider. While other parameters are designed for personal customization.


## 4. FAQ


