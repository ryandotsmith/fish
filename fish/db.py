from bsddb3 import db as bdb
from threading import Thread, Lock
import os, time, sys, shutil, argparse, string

SECOND = 1000000
statusMutex = Lock()

class DB:

  def __init__(self, dir, address, priority, buddy, wants_master, readonly):
    self.env = self.openEnv(dir, priority)
    if os.getenv("DEBUG"):
      self.env.set_verbose(bdb.DB_VERB_REPLICATION, True)
    if wants_master:
      print("at=wants-master addr=%s" % address)
      #Start the first master
      lh, _, lp = address.partition(':')
      site = self.env.repmgr_site(lh, int(lp))
      site.set_config(bdb.DB_LOCAL_SITE, True)
      site.set_config(bdb.DB_GROUP_CREATOR, True)
      site.close()

      self.env.repmgr_start(1, bdb.DB_REP_MASTER)
      self.db = bdb.DB(self.env).open('local', bdb.DB_HASH, bdb.DB_CREATE)
    else:
      print("at=wants-client addr=%s buddy=%s" % (address, buddy))

      lh, _, lp = address.partition(':')
      localSite = self.env.repmgr_site(lh, int(lp))
      localSite.set_config(bdb.DB_LOCAL_SITE, True)
      localSite.close()

      bh, _, bp = buddy.partition(':')
      helperSite = self.env.repmgr_site(bh, int(bp))
      helperSite.set_config(bdb.DB_BOOTSTRAP_HELPER, True)
      helperSite.close()

      self.env.repmgr_start(1, bdb.DB_REP_CLIENT)
      time.sleep(2)
      if readonly:
        self.db = bdb.DB(self.env).open('local', bdb.DB_HASH, bdb.DB_RDONLY)
      else:
        self.db = bdb.DB(self.env).open('local', bdb.DB_HASH)
    self.startReport()

  def eventCallback(self, dbenv, msg, notsure):
    print("at=rep-event msg=%s" % msg)
    if msg == bdb.DB_EVENT_REP_MASTER:
      print("at=elected-leader")
    elif msg == bdb.DB_EVENT_REP_CLIENT:
      print("at=elected-client")

  def openEnv(self, dir, priority):
    print("at=build-env dir=%s" % dir)
    env = bdb.DBEnv()
    env.open(dir, bdb.DB_CREATE | bdb.DB_RECOVER | bdb.DB_INIT_REP | bdb.DB_THREAD | bdb.DB_INIT_LOCK | bdb.DB_INIT_TXN | bdb.DB_INIT_MPOOL)
    env.rep_set_priority(priority)
    env.set_event_notify(self.eventCallback)
    env.rep_set_timeout(bdb.DB_REP_ELECTION_TIMEOUT, SECOND)
    env.rep_set_timeout(bdb.DB_REP_HEARTBEAT_MONITOR, SECOND)
    env.rep_set_timeout(bdb.DB_REP_HEARTBEAT_SEND, int(SECOND/2))
    return(env)

  def startReport(self):
    def printReport(d):
      while True:
        time.sleep(2)
        if d.is_master():
          print('role=master master=%s' % d.master_address())
        else:
          print('role=client master=%s' % d.master_address())
    t = Thread(target=printReport, args=(self,))
    t.daemon = True #handle signals
    t.start()


  def is_master(self):
    return(self.status()['status'] == 2)

  def master_address(self):
    host, port = self.master().get_address()
    return('%s:%d' % (host, port))

  def master(self):
    meid = self.status()['master']
    return(self.env.repmgr_site_by_eid(meid))

  def status(self):
    statusMutex.acquire()
    try:
      return(self.env.rep_stat())
    finally:
      statusMutex.release()
