"""
BitBake "Fetch" gh (GitHub) implementation

"""

# Copyright (C) 2024 HBK
#
# Based on repo.py which is:
# Copyright (C) 2009 Tom Rini <trini@embeddedalley.com>
#
# SPDX-License-Identifier: GPL-2.0-only
#

import os
import bb
from bb.fetch2 import FetchError
from bb.fetch2 import FetchMethod
from bb.fetch2 import runfetchcmd

class Gh(FetchMethod):
    """Class to fetch a release or CI file from GitHub using gh"""

    def supports(self, ud, d):
        """
        Check to see if a given url can be fetched with gh.
        """
        return ud.type in ['ghrel']

    def urldata_init(self, ud, d):
        path = ud.url.split("://")[1].split(";")[0]
        parts = path.split("/")
        ud.owner = parts[0]
        ud.reponame = parts[1]
        ud.rel = parts[2]
        ud.file = parts[3]
        ud.basename = ud.file
        ud.localfile = ud.basename
        ud.basecmd = d.getVar("FETCHCMD_gh") or "/usr/bin/env gh release download"

    def download(self, ud, d):
        cmd = '%s -R %s/%s %s -p %s -O %s' % (ud.basecmd, ud.owner, ud.reponame, ud.rel, ud.file, ud.localpath)
        bb.fetch2.check_network_access(d, cmd, ud.url)
        runfetchcmd(cmd, d)

        if not os.path.exists(ud.localpath):
            raise FetchError("The gh release download command returned success for %s but %s doesn't exist?!" % (ud.url, ud.localpath))

        if os.path.getsize(ud.localpath) == 0:
            os.remove(ud.localpath)
            raise FetchError("The gh release download command for %s resulted in a zero size file?! Deleting and failing since this isn't right." % (ud.url))

        return True

    def checkstatus(self, fetch, ud, d):
        cmd = '%s -R %s/%s %s -p %s -O /dev/null' % (ud.basecmd, ud.owner, ud.reponame, ud.rel, ud.file)
        bb.fetch2.check_network_access(d, cmd, ud.url)
        runfetchcmd(cmd, d)
        return True
