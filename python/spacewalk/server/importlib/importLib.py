#  pylint: disable=missing-module-docstring,invalid-name
#
# Copyright (c) 2008--2018 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#
#
# Common data structures used throughout the import code
#

import os
import shutil
from uyuni.common.usix import IntType, StringType, InstanceType

try:
    #  python 2
    # pylint: disable-next=unused-import
    from UserDict import UserDict
    from UserList import UserList
except ImportError:
    #  python3
    from collections import UserList, UserDict

# pylint: disable-next=ungrouped-imports
from uyuni.common.checksum import getFileChecksum
from uyuni.common.fileutils import createPath
from spacewalk.common.rhnConfig import CFG

# no-op class, used to define the type of an attribute


class DateType:
    pass


# An Item is just an extension for a dictionary
class Item(dict):

    """
    First level object, that stores information in a hash-like structure
    """

    def __init__(self, attributes=None):
        dict.__init__(self, attributes)

    # pylint: disable-next=redefined-builtin
    def populate(self, hash):
        self.update(hash)
        return self

    def __repr__(self):
        # pylint: disable-next=consider-using-f-string
        return "[<%s instance; attributes=%s]" % (
            str(self.__class__),
            dict.__repr__(self),
        )


# BaseInformation is an Item with a couple of other features (an id, an ignored
# flag, diff information)


class BaseInformation(Item):

    """
    Second level object. It may contain composite items as attributes
    """

    # pylint: disable-next=redefined-builtin
    def __init__(self, dict=None):
        Item.__init__(self, dict)
        # Initialize attributes
        for k in list(dict.keys()):
            self[k] = None
        # Each information object has an id (which is set by the database)
        self.id = None
        # If the information is ignored (non-critical)
        self.ignored = None
        # Diff with the object already installed
        self.diff = None
        # Same as above, except that it doesn't get cleared if the upload was
        # forced
        self.diff_result = None

    def toDict(self):
        # pylint: disable-next=redefined-builtin
        dict = {
            # pylint: disable-next=unnecessary-negation
            "ignored": not not self.ignored,
            "diff": self.diff.toDict(),
        }
        return dict


# This class is handy for reducing code duplication


class Information(BaseInformation):
    attributeTypes = {}

    def __init__(self):
        BaseInformation.__init__(self, self.attributeTypes)


# Function that validates the insertion of items in a Collection


def validateInformation(obj):
    if not isinstance(obj, BaseInformation):
        if isinstance(obj, InstanceType):
            # pylint: disable-next=consider-using-f-string
            strtype = "instance of %s" % obj.__class__
        else:
            strtype = str(type(obj))
        # pylint: disable-next=consider-using-f-string
        raise TypeError("Expected an Information object; got %s" % strtype)


# A list with the needed functions to validate what gets put in it
# pylint: disable-next=missing-class-docstring
class Collection(UserList):
    # pylint: disable-next=redefined-builtin
    def __init__(self, list=None):
        if list:
            for obj in list:
                validateInformation(obj)
        UserList.__init__(self, list)

    def __setitem__(self, i, item):
        validateInformation(item)
        UserList.__setitem__(self, i, item)

    def append(self, item):
        validateInformation(item)
        UserList.append(self, item)

    add = append

    def insert(self, i, item):
        validateInformation(item)
        UserList.insert(self, i, item)

    def extend(self, other):
        for obj in other:
            validateInformation(obj)
        UserList.extend(self, other)

    def __setslice__(self, i, j, other):
        for obj in other:
            validateInformation(obj)
        UserList.__setslice__(self, i, j, other)

    def __add__(self, other):
        for obj in other:
            validateInformation(obj)
        UserList.__add__(self, other)

    def __radd__(self, other):
        for obj in other:
            validateInformation(obj)
        UserList.__radd__(self, other)

    def __repr__(self):
        # pylint: disable-next=consider-using-f-string
        return "[<%s instance; items=%s]" % (str(self.__class__), str(self.data))


# Import classes
# XXX makes sense to put this in a different file
class ChannelFamily(Information):
    attributeTypes = {
        "name": StringType,
        "label": StringType,
        "product_url": StringType,
        "channels": [StringType],
        "org_id": IntType,
    }


class DistChannelMap(Information):
    attributeTypes = {
        "os": StringType,
        "release": StringType,
        "channel_arch": StringType,
        "channel": StringType,
        "org_id": IntType,
    }


class SupportInformation(Information):
    attributeTypes = {
        "pkgid": StringType,
        "keyword": StringType,
        "channel": StringType,
    }


class SuseProduct(Information):
    attributeTypes = {
        "name": StringType,
        "version": StringType,
        "friendly_name": StringType,
        "arch": StringType,
        "release": StringType,
        "product_id": IntType,
        "free": StringType,
        "base": StringType,
        "release_stage": StringType,
        "channel_family_label": StringType,
    }


class SuseProductChannel(Information):
    attributeTypes = {
        "product_id": IntType,
        "channel_id": IntType,
        "mandatory": StringType,
    }


class SuseUpgradePath(Information):
    attributeTypes = {
        "from_pdid": IntType,
        "to_pdid": IntType,
    }


class SuseProductExtension(Information):
    attributeTypes = {
        "product_id": IntType,
        "root_id": IntType,
        "ext_id": IntType,
        "recommended": StringType,
    }


class SuseProductRepository(Information):
    attributeTypes = {
        "product_id": IntType,
        "rootid": IntType,
        "repo_id": IntType,
        "channel_label": StringType,
        "parent_channel_label": StringType,
        "channel_name": StringType,
        "mandatory": StringType,
        "update_tag": StringType,
    }


class SCCRepository(Information):
    attributeTypes = {
        "sccid": IntType,
        "autorefresh": StringType,
        "name": StringType,
        "distro_target": StringType,
        "description": StringType,
        "url": StringType,
        "signed": StringType,
        "installer_updates": StringType,
    }


class SuseSubscription(Information):
    attributeTypes = {
        "max_members": IntType,  # Deprecated
        "org_id": IntType,
        "channel_family_id": IntType,
        "group_type": IntType,
    }


class ClonedChannel(Information):
    attributeTypes = {
        "orig": StringType,
        "orig_id": IntType,
        "clone": StringType,
        "id": IntType,
    }


class ReleaseChannelMap(Information):
    attributeTypes = {
        "product": StringType,
        "version": StringType,
        "release": StringType,
        "channel_arch_id": IntType,
        "channel_id": IntType,
    }


class ChannelErratum(Information):
    attributeTypes = {
        "id": StringType,
        "advisory_name": StringType,
        "last_modified": DateType,
    }


class IncompleteSourcePackage(Information):
    attributeTypes = {
        "id": StringType,
        "source_rpm": StringType,
        "last_modified": DateType,
    }


class ChannelTrust(Information):
    attributeTypes = {
        "org_trust_id": IntType,
    }


class ContentSourceSsl(Information):
    attributeTypes = {
        "ssl_ca_cert_id": IntType,
        "ssl_client_cert_id": IntType,
        "ssl_client_key_id": IntType,
    }


class ContentSource(Information):
    attributeTypes = {
        "label": StringType,
        "source_url": StringType,
        "type_id": IntType,
        "org_id": IntType,
        "ssl-sets": [ContentSourceSsl],
        "channels": [StringType],
    }


class Channel(Information):
    attributeTypes = {
        "label": StringType,
        "org_id": IntType,
        "channel_arch": StringType,
        "parent_channel": StringType,
        "name": StringType,
        "summary": StringType,
        "description": StringType,
        "last_modified": DateType,
        "comps_last_modified": DateType,
        "modules_last_modified": DateType,
        "gpg_key_url": StringType,
        "update_tag": StringType,
        "installer_updates": StringType,
        "product_name_id": IntType,
        "channel_product_id": IntType,
        "receiving_updates": StringType,
        "checksum_type": StringType,  # xml dumps >= 3.5
        "channel_access": StringType,
        # XXX Not really useful stuff
        "basedir": StringType,
        "product_name": StringType,
        "product_version": StringType,
        "product_beta": StringType,
        # Families this channel is subscribed to
        "families": [ChannelFamily],
        "packages": [StringType],
        "source_packages": [IncompleteSourcePackage],
        "all-packages": [StringType],
        "dists": [DistChannelMap],
        "release": [ReleaseChannelMap],
        "errata": [StringType],
        "errata_timestamps": [ChannelErratum],
        "kickstartable_trees": [StringType],
        "trust_list": [ChannelTrust],
        "export-type": StringType,
        "export-end-date": StringType,
        "export-start-date": StringType,
        "content-sources": [ContentSource],
    }


class OrgTrust(Information):
    attributeTypes = {
        "org_id": IntType,
    }


class Org(Information):
    attributeTypes = {
        "id": IntType,
        "name": StringType,
        "org_trust_ids": [OrgTrust],
    }


# pylint: disable-next=missing-class-docstring
class File(Item):
    attributeTypes = {
        "name": StringType,
        "device": IntType,
        "inode": IntType,
        "file_mode": IntType,
        "username": StringType,
        "groupname": StringType,
        "rdev": IntType,
        "file_size": IntType,
        "mtime": DateType,
        "linkto": StringType,
        "flags": IntType,
        "verifyflags": IntType,
        "lang": StringType,
        "checksum": StringType,
        "checksum_type": StringType,
    }

    def __init__(self):
        Item.__init__(self, self.attributeTypes)


class Dependency(Item):
    attributeTypes = {
        "name": StringType,
        "version": StringType,
        "flags": IntType,
    }

    def __init__(self):
        Item.__init__(self, self.attributeTypes)


class ChangeLog(Item):
    attributeTypes = {
        "name": StringType,
        "text": StringType,
        "time": DateType,
    }

    def __init__(self):
        Item.__init__(self, self.attributeTypes)


class Checksum(Item):
    attributeTypes = {
        "type": StringType,
        "value": StringType,
    }

    def __init__(self):
        Item.__init__(self, self.attributeTypes)


class ProductFile(Information):
    attributeTypes = {
        "name": StringType,
        "epoch": StringType,
        "version": StringType,
        "release": StringType,
        "arch": StringType,
        "vendor": StringType,
        "summary": StringType,
        "description": StringType,
    }


class Eula(Information):
    attributeTypes = {
        "text": StringType,
        "checksum": StringType,
    }


class ExtraTag(Information):
    attributeTypes = {
        "name": StringType,
        "value": StringType,
    }


# pylint: disable-next=missing-class-docstring
class IncompletePackage(BaseInformation):
    attributeTypes = {
        "package_id": StringType,  # RH db id
        "name": StringType,
        "epoch": StringType,
        "version": StringType,
        "release": StringType,
        "arch": StringType,
        "org_id": IntType,
        "package_size": IntType,
        "last_modified": DateType,
        "md5sum": StringType,  # xml dumps < 3.5
        # These attributes are lists of objects
        "channels": [StringType],
        "checksum_list": [Checksum],
    }

    def __init__(self):
        BaseInformation.__init__(self, IncompletePackage.attributeTypes)
        self.name = None
        self.evr = None
        self.arch = None
        self.org_id = None

    def toDict(self):
        # pylint: disable-next=redefined-builtin
        dict = BaseInformation.toDict(self)
        evr = list(self.evr)
        if evr[0] is None:
            evr[0] = ""

        dict["name"] = self.name
        dict["evr"] = evr
        dict["arch"] = self.arch

        org_id = self.org_id
        if org_id is None:
            org_id = ""
        dict["org_id"] = org_id
        return dict

    def short_str(self):
        # pylint: disable-next=consider-using-f-string,unsubscriptable-object
        return "%s-%s-%s.%s.rpm" % (self.name, self.evr[1], self.evr[2], self.arch)


class Package(IncompletePackage):

    """
    A package is a hash of attributes
    """

    attributeTypes = {
        "description": StringType,
        "summary": StringType,
        "license": StringType,
        "package_group": StringType,
        "rpm_version": StringType,
        "payload_size": IntType,
        "installed_size": IntType,
        "payload_format": StringType,
        "build_host": StringType,
        "build_time": DateType,
        "cookie": StringType,
        "vendor": StringType,
        "source_rpm": StringType,
        "package_size": IntType,
        "last_modified": DateType,
        "sigpgp": StringType,
        "siggpg": StringType,
        "sigsize": IntType,
        "header_start": IntType,
        "header_end": IntType,
        "path": StringType,
        "md5sum": StringType,  # xml dumps < 3.5
        "sigmd5": StringType,
        # These attributes are lists of objects
        "files": [File],
        "requires": [Dependency],
        "provides": [Dependency],
        "conflicts": [Dependency],
        "obsoletes": [Dependency],
        "recommends": [Dependency],
        "supplements": [Dependency],
        "enhances": [Dependency],
        "suggests": [Dependency],
        "breaks": [Dependency],
        "predepends": [Dependency],
        "changelog": [ChangeLog],
        "channels": [StringType],
        "checksum_list": [Checksum],
        "product_files": [ProductFile],
        "eulas": [Eula],
        "extra_tags": [ExtraTag],
    }

    def __init__(self):
        # Inherit from IncompletePackage
        IncompletePackage.__init__(self)
        # And initialize the specific ones
        for k in list(self.attributeTypes.keys()):
            self[k] = None


# pylint: disable-next=missing-class-docstring
class SourcePackage(IncompletePackage):
    attributeTypes = {
        "package_group": StringType,
        "rpm_version": StringType,
        "source_rpm": StringType,
        "payload_size": IntType,
        "payload_format": StringType,
        "build_host": StringType,
        "build_time": DateType,
        "vendor": StringType,
        "cookie": StringType,
        "package_size": IntType,
        "path": StringType,
        "last_modified": DateType,
        # these attributes are mutualy exclusive
        "md5sum": StringType,  # xml dumps < 3.5
        "sigmd5": StringType,  # xml dumps < 3.5 and rpms
        "checksum_list": [Checksum],
    }

    def __init__(self):
        # Inherit from IncompletePackage
        IncompletePackage.__init__(self)
        # And initialize the specific ones
        self.source_rpm = None
        for k in list(self.attributeTypes.keys()):
            self[k] = None

    def short_str(self):
        return self.source_rpm


class Bug(Information):
    attributeTypes = {
        "bug_id": StringType,
        "summary": StringType,
        "href": StringType,
    }


class ErrataFile(Information):
    attributeTypes = {
        "filename": StringType,
        "file_type": StringType,
        "channel_list": [StringType],
        "package_id": IntType,
        # these attributes are mutualy exclusive
        "md5sum": StringType,  # xml dumps < 3.5
        "checksum_list": [Checksum],
    }


class Keyword(Information):
    attributeTypes = {
        "keyword": StringType,
    }


class Erratum(Information):
    attributeTypes = {
        "advisory": StringType,
        "advisory_name": StringType,
        "advisory_rel": IntType,
        "advisory_type": StringType,
        "advisory_status": StringType,
        "product": StringType,
        "description": StringType,
        "synopsis": StringType,
        "topic": StringType,
        "solution": StringType,
        "issue_date": DateType,
        "update_date": DateType,
        "last_modified": DateType,
        "notes": StringType,
        "org_id": IntType,
        "refers_to": StringType,
        "severity": StringType,
        "errata_from": StringType,
        # These attributes are lists of objects
        "channels": [Channel],
        "packages": [IncompletePackage],
        "files": [ErrataFile],
        "keywords": [Keyword],
        "bugs": [Bug],
        "cve": [StringType],
        "severity_id": IntType,
    }


class BaseArch(Information):
    attributeTypes = {
        "label": StringType,
        "name": StringType,
    }


class CPUArch(BaseArch):
    pass


class BaseTypedArch(BaseArch):
    attributeTypes = BaseArch.attributeTypes.copy()
    attributeTypes.update(
        {
            "arch-type-label": StringType,
            "arch-type-name": StringType,
        }
    )


class ServerArch(BaseTypedArch):
    pass


class PackageArch(BaseTypedArch):
    pass


class ChannelArch(BaseTypedArch):
    pass


class ServerPackageArchCompat(Information):
    attributeTypes = {
        "server-arch": StringType,
        "package-arch": StringType,
        "preference": IntType,
    }


class ServerChannelArchCompat(Information):
    attributeTypes = {
        "server-arch": StringType,
        "channel-arch": StringType,
    }


class ChannelPackageArchCompat(Information):
    attributeTypes = {
        "channel-arch": StringType,
        "package-arch": StringType,
    }


class ServerGroupServerArchCompat(Information):
    attributeTypes = {
        "server-arch": StringType,
        "server-group-type": StringType,
    }


class KickstartFile(Information):
    attributeTypes = {
        "relative_path": StringType,
        "last_modified": DateType,
        "file_size": IntType,
        "md5sum": StringType,  # xml dumps < 3.5
        "checksum_list": [Checksum],
    }


class KickstartableTree(Information):
    # pylint: disable-next=duplicate-key,duplicate-key
    attributeTypes = {
        "label": StringType,
        "base_path": StringType,
        "channel": StringType,
        "boot_image": StringType,
        "kstree_type_label": StringType,
        "install_type_name": StringType,
        "kstree_type_label": StringType,
        "install_type_name": StringType,
        "org_id": IntType,
        "last_modified": DateType,
        "files": [KickstartFile],
    }


class ProductName(Information):
    attributeTypes = {
        "label": StringType,
        "name": StringType,
    }


# Generic error object
class Error(Information):
    attributeTypes = {
        "error": StringType,
    }


# Base import class
# pylint: disable-next=missing-class-docstring
class Import:
    def __init__(self, batch, backend):
        self.batch = batch
        self.backend = backend
        # Upload force
        self.uploadForce = 1
        # Force object verification
        self.forceVerify = 0
        # Ignore already-uploaded objects
        self.ignoreUploaded = 0
        # Transactional behaviour
        self.transactional = 0

    def setUploadForce(self, value):
        self.uploadForce = value

    def setForceVerify(self, value):
        self.forceVerify = value

    def setIgnoreUploaded(self, value):
        self.ignoreUploaded = value

    def setTransactional(self, value):
        self.transactional = value

    # This is the generic API exposed by an importer
    def preprocess(self):
        pass

    def fix(self):
        pass

    def submit(self):
        pass

    def run(self):
        self.preprocess()
        self.fix()
        self.submit()

    def cleanup(self):
        # Clean up the objects in the batch
        # pylint: disable-next=redefined-builtin
        for object in self.batch:
            self._cleanup_object(object)

    # pylint: disable-next=redefined-builtin
    def _cleanup_object(self, object):
        object.clear()

    def status(self):
        # Report the status back
        self.cleanup()
        return self.batch

    def _processPackage(self, package):
        # Build the helper data structures
        evr = []
        for f in ("epoch", "version", "release"):
            evr.append(package[f])
        package.evr = tuple(evr)
        package.name = package["name"]
        package.arch = package["arch"]
        package.org_id = package["org_id"]

    def _fix_encoding(self, text):
        if text is None:
            return None
        elif isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            try:
                return text.decode("utf8")
            # pylint: disable-next=bare-except
            except:
                return text.decode("iso8859-1")


# Any package processing import class
# pylint: disable-next=missing-class-docstring
class GenericPackageImport(Import):
    def __init__(self, batch, backend):
        Import.__init__(self, batch, backend)
        # Packages have to be pre-processed
        self.names = {}
        self.evrs = {}
        self.checksums = {}
        self.package_arches = {}
        self.channels = {}
        self.channel_package_arch_compat = {}

    def _processPackage(self, package):
        Import._processPackage(self, package)

        # Save the fields in the local hashes
        if package.evr not in self.evrs:
            self.evrs[package.evr] = None

        if package.name not in self.names:
            self.names[package.name] = None

        if package.arch not in self.package_arches:
            self.package_arches[package.arch] = None

        # pylint: disable-next=redefined-builtin
        for type, chksum in list(package["checksums"].items()):
            checksumTuple = (type, chksum)
            # pylint: disable-next=unnecessary-negation
            if not checksumTuple in self.checksums:
                self.checksums[checksumTuple] = None

    def _postprocessPackageNEVRA(self, package):
        arch = self.package_arches[package.arch]
        if not arch:
            # Unsupported arch
            package.ignored = 1
            # pylint: disable-next=consider-using-f-string
            raise InvalidArchError(package.arch, "Unknown arch %s" % package.arch)

        #        package['package_arch_id'] = arch
        #        package['name_id'] = self.names[package.name]
        #        package['evr_id'] = self.evrs[package.evr]

        nevra = (self.names[package.name], self.evrs[package.evr], arch)
        nevra_dict = {nevra: None}

        self.backend.lookupPackageNEVRAs(nevra_dict)

        package["name_id"], package["evr_id"], package["package_arch_id"] = nevra
        package["nevra_id"] = nevra_dict[nevra]
        package["checksum_id"] = self.checksums[
            (package["checksum_type"], package["checksum"])
        ]


# Exceptions


class ImportException(Exception):
    def __init__(self, arglist):
        Exception.__init__(self, *arglist)


class AlreadyUploadedError(ImportException):
    # pylint: disable-next=redefined-builtin
    def __init__(self, object, *rest):
        ImportException.__init__(self, rest)
        self.object = object


class FileConflictError(AlreadyUploadedError):
    pass


class InvalidPackageError(ImportException):
    def __init__(self, package, *rest):
        ImportException.__init__(self, rest)
        self.package = package


class InvalidArchError(ImportException):
    def __init__(self, arch, *rest):
        ImportException.__init__(self, rest)
        self.arch = arch


class InvalidChannelError(ImportException):
    def __init__(self, channel, *rest):
        ImportException.__init__(self, rest)
        self.channel = channel


class MissingParentChannelError(ImportException):
    def __init__(self, channel, *rest):
        ImportException.__init__(self, rest)
        self.channel = channel


class InvalidChannelFamilyError(ImportException):
    def __init__(self, channel_family, *rest):
        ImportException.__init__(self, rest)
        self.channel_family = channel_family


class IncompatibleArchError(ImportException):
    def __init__(self, arch1, arch2, *rest):
        ImportException.__init__(self, rest)
        self.arch1 = arch1
        self.arch2 = arch2


class TransactionError(ImportException):
    def __init__(self, *rest):
        ImportException.__init__(self, rest)


# Class that stores diff information


# pylint: disable-next=missing-class-docstring
class Diff(UserList):
    def __init__(self):
        UserList.__init__(self)
        self.level = 0

    def setLevel(self, level):
        if self.level < level:
            self.level = level

    def toDict(self):
        # Converts the object to a dictionary
        l = []
        for item in self:
            l.append(removeNone(item))
        return {
            "level": self.level,
            "diff": l,
        }


# Replaces all occurences of None with the empty string
# pylint: disable-next=redefined-builtin
def removeNone(list):
    return [(x is not None and x) or "" for x in list]


# Assorted functions for various things


def move_package(filename, basedir, relpath, checksum_type, checksum, force=None):
    """
    Copies the information from the file descriptor to a file
    Checks the file's checksum, raising FileConflictErrror if it's different
    The force flag prevents the exception from being raised, and copies the
    file even if the checksum has changed
    """
    packagePath = basedir + "/" + relpath
    # Is the file there already?
    if os.path.isfile(packagePath):
        if force:
            os.unlink(packagePath)
        else:
            # Get its checksum
            localsum = getFileChecksum(checksum_type, packagePath)
            if checksum == localsum:
                # Same file, so get outa here
                return
            raise FileConflictError(os.path.basename(packagePath))

    # pylint: disable-next=redefined-builtin
    dir = os.path.dirname(packagePath)
    # Create the directory where the file will reside
    if not os.path.exists(dir):
        createPath(dir)

    # Check if the RPM has been downloaded from a remote repository
    # If so, it is stored in CFG.MOUNT_POINT and we have to move it
    # If not, the repository is local to the server, so the rpm should be copied
    if filename.startswith(CFG.MOUNT_POINT):
        shutil.move(filename, packagePath)
    else:
        shutil.copy(filename, packagePath)

    # set the path perms readable by all users
    os.chmod(packagePath, int("0644", 8))


# Returns a list of containing nevra for the given RPM header
NEVRA_TAGS = ["name", "epoch", "version", "release", "arch"]


def get_nevra(header):
    # Get nevra
    nevra = []
    for tag in NEVRA_TAGS:
        nevra.append(header[tag])
    return nevra


def get_nevra_dict(header):
    # Get nevra
    nevra = {}
    for tag in NEVRA_TAGS:
        nevra[tag] = header[tag]
    if nevra["epoch"] == "":
        nevra["epoch"] = None
    return nevra
