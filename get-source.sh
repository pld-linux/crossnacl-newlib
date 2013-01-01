#!/bin/sh
# Make snapshot of nacl-binutils
# Author: Elan Ruusamäe <glen@pld-linux.org>
set -e

# Generated from git
# git clone http://git.chromium.org/native_client/nacl-newlib.git
# (Checkout ID taken from chromium-15.0.874.106/native_client/tools/REVISIONS)
# cd nacl-newlib
# git checkout f5185a5726155efb578d4d0f6537bc15ee5edb7d
# cd ..
# For newlib version, grep PACKAGE_VERSION newlib/libm/configure
# mv nacl-newlib nacl-newlib-1.18.0-gitf5185a57
# tar cfj nacl-newlib-1.18.0-gitf5185a57.tar.bz2 nacl-newlib-1.18.0-gitf5185a57

package=nacl-newlib
repo_url=http://git.chromium.org/native_client/$package.git
nacl_trunk=http://src.chromium.org/native_client/trunk
omahaproxy_url=http://omahaproxy.appspot.com
specfile=crossnacl-newlib.spec

# if you get errors that sha1 hash not found, try increasing depth
# fatal: Path 'gcc/BASE-VER' does not exist in 'c69a5b7252d2f073d0f526800e4fca3b63cd1fab'
depth=

chrome_channel=${1:-stable}
chrome_version=$(curl -s "$omahaproxy_url/all?os=linux&channel=$chrome_channel" | awk -F, 'NR > 1{print $3}')
test -n "$chrome_version"
chrome_revision=$((echo 'data='; curl -s $omahaproxy_url/revision.json?version=$chrome_version; echo ',print(data.chromium_revision)') | js)
test -n "$chrome_revision"
chrome_branch=$(IFS=.; set -- $chrome_version; echo $3)
test -s DEPS.py || svn cat http://src.chromium.org/chrome/branches/$chrome_branch/src/DEPS@$chrome_revision > DEPS.py
nacl_revision=$(awk -F'"' '/nacl_revision.:/{print $4}' DEPS.py)
test -n "$nacl_revision"

export GIT_DIR=$package.git

if [ ! -d $GIT_DIR ]; then
	install -d $GIT_DIR
	git init --bare
	git remote add origin $repo_url
	git fetch ${depth:+--depth $depth} origin refs/heads/master:refs/remotes/origin/master
else
	git fetch origin refs/heads/master:refs/remotes/origin/master
fi

# get src/native_client/tools/REVISIONS directly from svn
test -n "$nacl_revision"
test -s NACL_REVISIONS.sh || svn cat $nacl_trunk/src/native_client/tools/REVISIONS@$nacl_revision > NACL_REVISIONS.sh

if grep -Ev '^(#|(LINUX_HEADERS_FOR_NACL|NACL_(BINUTILS|GCC|GDB|GLIBC|NEWLIB))_COMMIT=[0-9a-f]+$|)' NACL_REVISIONS.sh >&2; then
	echo >&2 "I refuse to execute grabbed file for security concerns"
	exit 1
fi
. ./NACL_REVISIONS.sh

githash=$NACL_NEWLIB_COMMIT
git show $githash:newlib/libm/configure > configure
version=$(awk -F"'" '/PACKAGE_VERSION=/{print $2}' configure)
shorthash=$(git rev-parse --short $githash)
prefix=$package-$version-git$shorthash
archive=$prefix.tar.xz

if [ -f $archive ]; then
	echo "Tarball $archive already exists at $shorthash"
else
	git -c tar.tar.xz.command="xz -9c" archive $githash --prefix $prefix/ -o $archive

	../dropin $archive
fi

# We need to copy some missing header files from chromium
# mkdir ~/nacl-headers-15.0.874.106
# cd chromium-15.0.874.106/native_client/
# ./src/trusted/service_runtime/export_header.py src/trusted/service_runtime/include ~/nacl-headers-15.0.874.106/
# cd ~/nacl-headers-15.0.874.106
# tar cfj ~/nacl-headers-15.0.874.106.tar.bz2 .

package=nacl-headers
prefix=$package-$chrome_version

if [ -f $prefix.tar.xz ]; then
	echo "Tarball $prefix.tar.xz already exists"
else
	svn co $nacl_trunk/src/native_client/src/trusted/service_runtime@$nacl_revision $package
	cd $package
	./export_header.py include ../$prefix
	cd ..
	tar -cf $prefix.tar --exclude-vcs $prefix
	xz -9 $prefix.tar
	../dropin $prefix.tar.xz
fi

# Taken from chromium-15.0.874.106/native_client/tools/newlib-libc-script
svn cat $nacl_trunk/src/native_client/tools/newlib-libc-script@$nacl_revision > newlib-libc-script

# Taken from chromium-15.0.874.106/native_client/src/untrusted/pthread/pthread.h
svn cat $nacl_trunk/src/native_client/src/untrusted/pthread/pthread.h@$nacl_revision > pthread.h

rm -f NACL_REVISIONS.sh DEPS.py configure
