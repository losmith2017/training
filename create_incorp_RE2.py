#!/usr/bin/python

import argparse
import os
import re
import time
import urlparse

from solaris_install import CalledProcessError, Popen, run

''' Solaris Release Engineering build script which creates a pkg
    repo containing the solaris-auto-install-incorporation package.
    The repo is created in the current directory, and is called:
    ai_incorp_pkg_repo.yyyymmdd-hhmmss
'''

# ----------------  Settings for Solaris RE  -----------------

# Solaris RE should pass --osnetrepo and --aipkgrepo, these are required args.

# The --osnetrepo option should be set to where the current RE build's
# ON pkgs are located.
#
#   --osnetrepo=http://ipkg.us.oracle.com/solaris12/minidev

# The --aipkgrepo options should be set to where the current RE build's
# AI Media pkg is located.
# For an SRU, if there is no media being created for this build, this should
# be set to where the most recent AI Media pkg is located (perhaps the
# support repo).
#
#   --aipkgrepo=http://ipkg.us.oracle.com/solaris12/minidev

# ------------------------------------------------------------

# Script settings
AI_PKG_NAME = 'install-image/solaris-auto-install'
INCORP_NAME = 'install-image/solaris-auto-install-incorporation'
OSNET = 'consolidation/osnet/osnet-incorporation'
PKG = "/usr/bin/pkg"
PKGREPO = "/usr/bin/pkgrepo"
PKGSEND = "/usr/bin/pkgsend"
REPO_NAME = "file://%s/ai_incorp_pkg_repo.%s" % \
    (os.getcwd(), time.strftime("%Y%m%d-%H%M%S"))


def get_pkg_version(package, repo=None):
    """ method to retrieve the version of a given package
    package - package whose version to retrieve
    repo - which repo to query
    """
    if not repo:
        raise SystemExit("get_pkg_version missing repo")
    print "\nRetrieving package version of %s from:\n%s" % (package, repo)
    cmd = [PKG, "list", "-Hafv", "-g", repo, package]
    proc = run(cmd)
    version_re = re.compile(r"^pkg.*?%s@(.*?):" % package)
    version = version_re.search(proc.stdout).group(1)
    print version
    return version


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build AI media "
                                     "incorporation package")
    parser.add_argument("--osnetrepo", required=True,
                        help="Location of current RE build's ON pkgs.")
    parser.add_argument("--aipkgrepo", required=True,
                        help="Location of current RE build's AI Media pkg. "
                             "For SRU, location of most recent AI Media pkg.")
    parser.add_argument("--publisher", default="solaris")
    parser.add_argument("--repo", default=REPO_NAME)
    args = parser.parse_args()

    OSNET_REPO = args.osnetrepo
    AI_PKG_REPO = args.aipkgrepo
    print "Starting at " + time.asctime()
    print "Using OSNET_REPO %s" % OSNET_REPO
    print "Using AI_PKG_REPO %s" % AI_PKG_REPO

    # Create the repository (as needed) if it's a local path (no scheme)
    # or file:/// scheme.
    print "\nCreating repository at %s" % args.repo
    scheme = urlparse.urlsplit(args.repo).scheme
    if scheme in ("file", ""):
        # Try to create the repo
        cmd = [PKGREPO, "create", args.repo]
        repo = run(cmd, check_result=Popen.ANY)

        if repo.returncode == 0:
            # New repo was created. Add the publisher and make it default
            cmd = [PKGREPO, "-s", args.repo, "add-publisher", args.publisher]
            run(cmd)
            cmd = [PKGREPO, "-s", args.repo, "set",
                   "publisher/prefix=%s" % args.publisher]
            run(cmd)

    # Get version of consolidation/osnet/osnet-incorporation
    incorp_version = get_pkg_version(OSNET, OSNET_REPO)

    # Get version of install-image/solaris-auto-install
    ai_pkg_version = get_pkg_version(AI_PKG_NAME, AI_PKG_REPO)

    # Generate incorporation pkg
    incorp_pkg_name = "pkg://%s/%s@%s" % \
        (args.publisher, INCORP_NAME, incorp_version)

    dep_pkg_name = "%s@%s" % (AI_PKG_NAME, ai_pkg_version)

    # Generate the manifest
    manifest = ('set name=pkg.fmri value=%(incorppkg)s\n'
                'depend type=incorporate fmri=%(depname)s'
                % {'incorppkg': incorp_pkg_name, 'depname': dep_pkg_name})

    print "\nManifest contents:\n%s" % manifest
    print "\nPublishing %s" % incorp_pkg_name
    cmd = [PKGSEND, "-s", args.repo, "publish"]
    pkgsend = Popen(cmd, stdin=Popen.PIPE, stdout=Popen.PIPE,
                    stderr=Popen.PIPE)
    stdout, stderr = pkgsend.communicate(manifest)
    if stderr.strip() or pkgsend.returncode:
        pkgsend.stdout = stdout
        pkgsend.stderr = stderr
        raise CalledProcessError(pkgsend.returncode, cmd, popen=pkgsend)
    else:
        print stdout.strip()

    # Refresh the repository
    cmd = [PKGREPO, "-s", args.repo, "refresh"]
    run(cmd)

    print "Finished at " + time.asctime()
