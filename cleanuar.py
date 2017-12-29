#!/usr/bin/python2.7

import argparse
import os
import sys

from lxml import etree
from urlparse import urlparse

from solaris_install import run, SetUIDasEUID, ApplicationData
from solaris_install.archive import LOGFILE
from solaris_install.archive.checkpoints import PrepareArchiveImage, \
    CreateArchiveDescriptor
from solaris_install.archive.ua_xml import xml_nsmap
from solaris_install.engine import InstallEngine

from subprocess import Popen, PIPE

CHROOT = '/usr/sbin/chroot'
PASSWD = '/usr/bin/passwd'
PKG = '/usr/bin/pkg'
RM = '/usr/bin/rm'
TOUCH = '/usr/bin/touch'
USERMOD = '/usr/sbin/usermod'
ZLOGIN = "/usr/sbin/zlogin"


def parse_cli():
    """Parse the CLI and pull off our options, if present. Make sure to pass
    through options meant of for 'archiveadm create' intact.

    """
    usage = \
        "Internal release utility which wraps archiveadm(1m) create.\n" \
        "Undocumented options are the same as with 'archiveadm create'.\n" \
        "Note the create subcommand must be used. All typical arguments\n" \
        "for 'archiveadm create' are passed along to archiveadm\n\n" \
        "All archives get a deeper image preparation than with the stock\n" \
        "library. All global zone (metal) and kernel zone) IPS publishers\n" \
        "are unset and the source host is set to a default. Users may\n" \
        "optionally pass a mock source host name as well as mock names\n" \
        "for zones.\n\n" \
        "Example:\n" \
        "# %s [clean options] create [archive options] archive.uar" % pname
    hh = \
        "Replace the source host's name in the archive."
    zmh = \
        "Given a list of 'zonename:mockname' sets, map the\n" \
        "real zonenames to the mocks in the final archive."
    sph = \
        "Given a list of 'uri:publisher' sets, set a list of\n" \
        "publishers in the archived global zones (non-global\n" \
        "zones have 'sysrepo')."
    examples = \
        "Option Examples:\n" \
        "\t--zone-mappings private1:public1,private2:public2\n" \
        "\t--set-publishers http://pkg.oracle.com/solaris11:solaris"

    parser = argparse.ArgumentParser(
                 description=usage,
                 formatter_class=argparse.RawTextHelpFormatter,
                 epilog=examples)

    group = parser.add_argument_group()
    parser.add_argument("create")
    group.add_argument("--source-host", action='store', help=hh)
    group.add_argument("--zone-mappings", action='append', help=zmh)
    group.add_argument("--set-publishers", action='append', help=sph)

    # Just parse the known args, we have all of archiveadm create's args to
    # pass along.
    arg_dict = vars(parser.parse_known_args()[0])

    # Confirm 'create' was passed. This should be called 'command' with a
    # value of 'create', but using 'create' as the key looks better in the
    # auto-generated usage.
    if not arg_dict.get('create') or arg_dict['create'] != 'create':
        sys.stderr.write("Must pass the 'create' command\n")
        parser.print_help()
        sys.exit(1)

    # Since we're passing control straight along to archiveadm, we need to
    # clean up sys.argv. This is a hack, but this whole thing is by
    # design. For each option, whack it along with its argument(s), if
    # present.
    if arg_dict.get('source_host'):
        sys.argv.remove('--source-host')
        sys.argv.remove(arg_dict.get('source_host'))

    if arg_dict.get('zone_mappings'):
        while '--zone-mappings' in sys.argv:
            sys.argv.remove('--zone-mappings')
        for arg in arg_dict.get('zone_mappings'):
            sys.argv.remove(arg)

    if arg_dict.get('set_publishers'):
        while '--set-publishers' in sys.argv:
            sys.argv.remove('--set-publishers')
        for arg in arg_dict.get('set_publishers'):
            sys.argv.remove(arg)

    # Before we return the argument dictionary, check for comma-separated
    # values and convert them to lists of strings.
    zone_mappings = arg_dict.get('zone_mappings')
    if zone_mappings and len(zone_mappings) == 1:
        if zone_mappings[0].find(',') != -1:
            arg_dict['zone_mappings'] = map(str, zone_mappings[0].split(','))

    set_publishers = arg_dict.get('set_publishers')
    if set_publishers and len(set_publishers) == 1:
        if set_publishers[0].find(',') != -1:
            arg_dict['set_publishers'] = map(str, set_publishers[0].split(','))
    return arg_dict


def monkeypatch_method(cls):
    """Utility function. Replaces a method in 'cls' with the decorated
    function. Replaces an existing method of the same name.

    """
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


def do_cmd(cmd, subprocess, zone):
    """Run the command in 'cmd' on the zone passed in 'zone'. If it's a kernel
    zone, zlogin. Otherwise, just run it in the executing environment, since
    for our purposes, we're working with altroots - non-global zone altroots
    are accessible in the executing context. Returns the Popen instance
    post-execution.

    # Any command that uses "*" wildcard needs to the shell parameter set
    # to true. The "run" command doesn't have the option for passing to
    # the shell variable, so use Popen instead.


    """
    if zone.brand == 'solaris-kz':
        zlogin_cmd = [ZLOGIN, '-U', zone.name]
        if subprocess == "popen":
            zlogin_cmd.extend(cmd[0])
            zlogin_cmd.extend(cmd[1])
        else:
            zlogin_cmd.extend(cmd)
        with SetUIDasEUID():
            return run(zlogin_cmd)
    else:
        if subprocess == "popen":
            return Popen("%s %s" % (cmd[0], cmd[1]), shell=True, stdin=PIPE, stdout=PIPE,
                    stderr=PIPE, close_fds=True) 
        else:
            return run(cmd)


def clean_image(instance):
    """Additional image prep work in order to come closer to a 'clean'
    archive image.

        * Reset the SMF configuration database
        * Destroy XML configuration in /etc/svc/profile/sysconfig* and site
        * Destroy root account shell history

    """
    print "\tRunning additional image cleanup...\n"
    for archive_object in instance.ua.archive_objects:
        altroot = archive_object._archive_be.mountpoint

        # Set up a list of commands to run. Use crappy CLI calls so we can
        # easily work over zlogin.
        #directories = ["etc/svc/profile/site/", "etc/svc/profile/volatile/",
        #               "etc/svc/profile/sysconfig"]
        #bash = ["root/.bash_history"]
        #messages = ["/var/adm/messages"]

        rmcmd = "%s -rf" % RM
        chroot_root = "%s %s %s -r files -d root" % (CHROOT, altroot, PASSWD)
        chroot_user = "%s %s %s -K type=normal root" %(CHROOT, altroot, USERMOD)

        cmds = []
        cmds.append((rmcmd, os.path.join(altroot, 'etc/svc/profile/site/*')))
        cmds.append((rmcmd, os.path.join(altroot, 'etc/svc/profile/volatile/*'))) 
        cmds.append((rmcmd, os.path.join(altroot, 'etc/svc/repository*')))
        cmds.append((rmcmd, os.path.join(altroot, 'root/.bash_history')))
        cmds.append((TOUCH, os.path.join(altroot, 'root/.bash_history')))
        cmds.append((rmcmd, os.path.join(altroot, 'var/adm/messages*')))
        cmds.append((TOUCH, os.path.join(altroot, 'var/adm/messages')))
        cmds.append((chroot_root,''))
        cmds.append((chroot_user, ''))

        for cmd in cmds:
            do_cmd(cmd, "popen", archive_object.zone)
    return


def reset_publishers(instance, new_pubs=[]):
    """Given a UnifiedArchive instance and list of publishers, replace all
    publishers set on all global zones. If the publishers list is empty,
    unset all publishers anyhow. Note non-global zones keep their 'sysrepo'
    setting.

    """
    # Regardless of whether publishers were passed in, unset all publishers in
    # all global zones. If publishers were passed, then set them.
    gzs = [ao for ao in instance.ua.archive_objects if ao.zone.is_global]
    for archive_object in gzs:
        print "\tModifying publishers for global zone '%s'...\n" % archive_object.zone.name
        altroot = archive_object._archive_be.mountpoint

        # Get the publishers list
        get_pubs = [PKG, "-R", altroot, "publisher", "-H", "-F", "tsv"]
        p = do_cmd(get_pubs, "run", archive_object.zone)
        publishers = " ".join([l.split()[0] for l in p.stdout.splitlines()])

        # Unset the entire list of publishers
        unset = [PKG, "-R", altroot, "unset-publisher", publishers]
        do_cmd(unset, "run", archive_object.zone)

        # If publishers were passed in, set them now. Use no-refresh in case
        # they are mock publishers, or otherwise inaccessible.
        for pub in new_pubs:
            # List of 'uri:publisher' strings passed in, set each pair
            uri, publisher = pub.rsplit(':', 1)
            set_pub = [PKG, "-R", altroot, "set-publisher", "--no-refresh",
                       "-g", uri, publisher]
            do_cmd(set_pub, "run", archive_object.zone)
    return


def set_source_host(instance, mockhost):
    """Given a UnifiedArchive instance and a mock hostname, set the mock in the
    archive image. This mock hostname will show up in 'archiveadm info' output
    of the resulting archive.

    """
    print "\tOverriding source hostname with '%s'...\n" % mockhost
    realhost = instance.ua.source_host

    # Walk the descriptor XML and swap all occurences of the actual source
    # hostname with our mock hostname. This only changes the descriptor info
    # in memory, not the instance UnifiedArchive.source_host data.
    for elem in instance.ua._descriptor._root.getiterator():
        if elem.text == realhost:
            elem.text = elem.text.replace(realhost, mockhost)
    return


def set_zonenames(instance, mapping):
    """Given a UnifiedArchive instance and a mapping dict, change all
    OVF descriptor references to real zonenames to the mocks they are mapped
    to. This will result in both zonenames listed in 'archiveadm info' output
    being mocked, as well as the zonecfg XML data attached to each zone.

    """
    # Walk the descriptor XML and mock out each of the VirtualSystem entries.
    # XXX Might be better to build iterators on the three cases of interest,
    # this is good enough for now.
    for elem in instance.ua._descriptor._root.getiterator():
        if elem.text in mapping:
            # Exact text match of one of our real names. This will be the
            # ovf:VirtualSystem ovf:Name element.
            realzone = elem.text
            mockzone = mapping[realzone]
            elem.text = elem.text.replace(realzone, mockzone)
            print "\tOverriding zonename '%s' with '%s'...\n" % (realzone, mockzone)
            continue

        if elem.get(xml_nsmap('ovf:id')) in mapping:
            # This will be either the ovf:VirtualSystem or
            # ovf:VirtualHardwareSection elements. Set the ovf:id with our
            # mockname.
            realzone = elem.get(xml_nsmap('ovf:id'))
            mockzone = mapping[realzone]
            elem.set(xml_nsmap('ovf:id'), mockzone)
            continue

        if elem.tag == xml_nsmap('ua:ZoneConfiguration'):
            # This is a zonecfg, check if it's one in our list
            if elem.get('name') in mapping:
                realzone = elem.get('name')
                mockzone = mapping[realzone]
                elem.set('name', mockzone)
                continue

        # XXX Missing zonepath possibly containing zonename... but that's
        # probably ok, really.

    return


def main():
    """Set up needed patches for 'archiveadm create' to achieve a more suitable
   'Oracle clean' version of a distributable archive, then invoke the create.

    """
    argd = parse_cli()

    # Patch the image prep checkpoint. This is where we can do a more thorough
    # cleanup of the image and unset all publishers in the image as well. If
    # replacement publishers were passed by the caller, we can set them here,
    # after the image is prepared.
    orig_prepare_image = PrepareArchiveImage.execute

    @monkeypatch_method(PrepareArchiveImage)
    def execute(instance, dry_run=False):

        # Start by calling the original PrepareArchiveImage.execute method
        orig_prepare_image(instance, dry_run)

        # Now run our tactical nuke to deep clean the image
        clean_image(instance)


        # Modify all global zone publishers. Unset all by default, set
        # replacement ones if passed.
        set_pubs = argd.get('set_publishers', [])
        reset_publishers(instance, set_pubs)
        return

    # Patch the descriptor creation checkpoint. Here we can swap the archived
    # zone names with fakes if we were passed a mapping. Also, set in a mock
    # source hostname if provided. Rather than save off the original and add to
    # it as we did with PrepareArchiveImage, we just override this one.
    @monkeypatch_method(CreateArchiveDescriptor)
    def execute(instance, dry_run=False):
        # Do the same as the stock checkpoint to get things started
        instance._parse_doc()
        instance.logger.debug("CreateArchiveDescriptor: UnifiedArchive [%s]",
                              instance.ua.uuid)
        instance.ua.generate_descriptor()

        # Now we've run generate_descriptor(), we have the descriptor XML ready
        # in memory. Before we commit it out to disk in the OVF file, modify it
        # as needed.

        # First mock the source host name in the descriptor. If one was not
        # provided, use a default of 'solaris'.
        set_source_host(instance, argd.get('source_host', 'solaris'))

        # If provided, mock up the zonenames with the ones passed in.
        zonemap = {}
        if argd.get('zone_mappings'):
            # If we have a list of zone mappings, create a dictionary from
            # them. Keys are original zonenames, values are the mocks.
            orig = [s.split(':')[0] for s in argd.get('zone_mappings')]
            mock = [s.split(':')[1] for s in argd.get('zone_mappings')]

            # Pass in the mock name mappings and override the real zonenames.
            set_zonenames(instance, dict(zip(orig, mock)))

        # Finally, commit the descriptor with the modified state.
        instance.ua.commit_descriptor()
        return

    # Begin the process of archive creation
    from solaris_install.archive import cli
    from solaris_install.archive.archive_operations import create_unified_archive

    # Since this operation is outside of the archiveadm framework, all of the
    # preliminary set up has to be done.
    install_engine = InstallEngine(LOGFILE)
    install_engine.doc.volatile.insert_children(
           ApplicationData("archive-cleanuar", logname=LOGFILE))
    print("\nLogging to %s\n") % LOGFILE
    subcommand, options, args = cli._parse_input()

    #obtain the path, check it, and make it an absolute path, if necessary.
    path = args[0]

    uri = urlparse(path, scheme='file')
    if uri.scheme != 'file':
        raise SystemExit(_("archiveadm create: file-based path required"))

    path = os.path.abspath(path)

    # For the time being, we will call the archive api directly. 
    create_unified_archive(path, zones=options.zones,
                             exclude_zones=options.exclude_zones,
                             exclude_ds=options.exclude_ds,
                             recovery=options.recovery,
                             skip_check=options.skip_check,
                             exclude_media=options.exclude_media,
                             root_only=options.root_only)


if __name__ == "__main__":
    pname = os.path.basename(sys.argv[0])
    main()
