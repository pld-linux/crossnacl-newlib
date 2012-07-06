%define		gitver 590577e
Summary:	C library intended for use on embedded systems
Name:		crossnacl-newlib
Version:	1.18.0
Release:	1.git%{gitver}
# Generated from git
# git clone http://git.chromium.org/native_client/nacl-newlib.git
# (Checkout ID taken from chromium-15.0.874.106/native_client/tools/REVISIONS)
# cd nacl-newlib
# git checkout f5185a5726155efb578d4d0f6537bc15ee5edb7d
# cd ..
# For newlib version, grep PACKAGE_VERSION newlib/libm/configure
# mv nacl-newlib nacl-newlib-1.18.0-gitf5185a57
# tar cfj nacl-newlib-1.18.0-gitf5185a57.tar.bz2 nacl-newlib-1.18.0-gitf5185a57
License:	BSD and MIT and LGPL v2+
Group:		Libraries
Source0:	nacl-newlib-%{version}-git%{gitver}.tar.bz2
# Source0-md5:	f1badf60c44a6dc13f41920a432716e8
# We need to copy some missing header files from chromium
# mkdir ~/nacl-headers-15.0.874.106
# cd chromium-15.0.874.106/native_client/
# ./src/trusted/service_runtime/export_header.py src/trusted/service_runtime/include ~/nacl-headers-15.0.874.106/
# cd ~/nacl-headers-15.0.874.106
# tar cfj ~/nacl-headers-15.0.874.106.tar.bz2 .
Source1:	nacl-headers-17.0.963.46.tar.bz2
# Source1-md5:	30182830b595020b3e24258556863d39
# Taken from chromium-15.0.874.106/native_client/tools/newlib-libc-script
Source2:	newlib-libc-script
# Taken from chromium-15.0.874.106/native_client/src/untrusted/pthread/pthread.h
Source3:	pthread.h
URL:		http://sourceware.org/newlib/
BuildRequires:	crossnacl-binutils
BuildRequires:	crossnacl-gcc
BuildRequires:	fslint
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		x86_64-nacl

%description
Newlib is a C library intended for use on embedded systems. It is a
conglomeration of several library parts, all under free software
licenses that make them easily usable on embedded products.

This is the nacl fork.

%prep
%setup -q -n nacl-newlib-%{version}-git%{?gitver}
cd newlib/libc/sys/nacl
tar xf %{SOURCE1}
cd -
cp -p %{SOURCE2} .

%build
export NEWLIB_CFLAGS="-O2 -D_I386MACH_ALLOW_HW_INTERRUPTS -DSIGNAL_PROVIDED -mtls-use-call"
%configure \
	--disable-libgloss \
	--enable-newlib-iconv \
	--enable-newlib-io-long-long \
	--enable-newlib-io-long-double \
	--enable-newlib-io-c99-formats \
	--enable-newlib-mb \
	libc_cv_initfinit_array=yes \
	CFLAGS="-O2" \
	CFLAGS_FOR_TARGET="$NEWLIB_CFLAGS" \
	CXXFLAGS_FOR_TARGET="$NEWLIB_CFLAGS" \
	--target=%{target}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Conflicts with binutils
%{__rm} -r $RPM_BUILD_ROOT%{_infodir}

# The default pthread.h doesn't work right?
%{__rm} $RPM_BUILD_ROOT%{_prefix}/%{target}/include/pthread.h
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_prefix}/%{target}/include/

# We have to hack up libc.a to get things working.
# 32bit
mv $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libc.a $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libcrt_common.a
sed "s/@OBJFORMAT@/elf32-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libc.a

# 64bit (default)
mv $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libc.a $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libcrt_common.a
sed "s/@OBJFORMAT@/elf64-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libc.a

# fix copies to be hardlinks (maybe should symlink in the future)
findup -m $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_datadir}/iconv_data
%{_prefix}/%{target}/include
%{_prefix}/%{target}/lib
