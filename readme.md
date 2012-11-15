# Fish

## The Problem

We wish to provide a transactional data store that offers distributed replication and automatic fail-over.

## A Solution

A proof of concept. Fish offers a service layer on top of BerkeleyDB. Fish explicity uses BDB's replication manager to create a fault-tolerant, distributed system.

The idea is to have a fleet of front-end services that receive PUT/GET requests via HTTP. The front-ends will remain uncoordinated. Furthermore each front-end will have a local, read-only BDB that is a part of the Fish replication group. To service an HTTP request, the front-end will use it's local BDB to resolve the back-end who is currently elected master. The front-end will connect directly to the master back-end and issue the request.

## Why Fish Matters

Fish leverages BerkelyDB which is a stable, mature & feature-full database. BDB offers a single Writer topology with a paxos implemented leader election manager. Furthermore, BDB offers granular control over data consistency. Transaction can be committed to a quorum, all-eligible-leaders, or all sites.

## Usage

```bash
$ git clone git://github.com/ryandotsmith/fish.git
$ cd fish
$ pip install -r requirements.txt
```

Start a master:

```bash
$ mkdir d0
$ python fish/web.py
```
