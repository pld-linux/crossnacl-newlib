%define		rel	1
%define		gitver	07af971
Summary:	C library intended for use on embedded systems - NaCl version
Summary(pl.UTF-8):	Biblioteka C przeznaczona dla systemów wbudowanych - wersja dla NaCl
Name:		crossnacl-newlib
Version:	2.0.0
Release:	0.git%{gitver}.%{rel}
License:	BSD and MIT and LGPL v2+
Group:		Libraries
Source0:	nacl-newlib-%{version}-git%{gitver}.tar.xz
# Source0-md5:	2e8b05e7ebe9eefa3e0d3f6d0ab23a1e
Source1:	nacl-headers-33.0.1750.117.tar.xz
# Source1-md5:	26f4e73044f01cbe0b89bec7fa4deea1
Source2:	newlib-libc-script
Source3:	pthread.h
Source4:	get-source.sh
URL:		http://sourceware.org/newlib/
BuildRequires:	crossnacl-binutils
BuildRequires:	crossnacl-gcc
BuildRequires:	fslint
BuildRequires:	python-modules
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		x86_64-nacl
%define		archprefix	%{_prefix}/%{target}
%define		archincludedir	%{archprefix}/include
%define		archlibdir	%{archprefix}/lib
%define		archlib32dir	%{archprefix}/lib32
%define		archlib64dir	%{archprefix}/lib64

%description
Newlib is a C library intended for use on embedded systems. It is a
conglomeration of several library parts, all under free software
licenses that make them easily usable on embedded products.

This is the NaCl fork.

%description -l pl.UTF-8
Newlib to biblioteka C przeznaczona dla systemów wbudowanych. Jest
połączeniem kilku części biblioteki, wszystkich na wolnych licencjach
pozwalających na łatwe użycie w produktach wbudowanych.

Ten pakiet zawiera odgałęzienie dla platformy NaCl.

%prep
%setup -q -n nacl-newlib-%{version}-git%{?gitver}
tar -xvf %{SOURCE1} -C newlib/libc/sys/nacl --strip-components=1
cp -p %{SOURCE2} .

%{__rm} etc/*.texi

%build
export NEWLIB_CFLAGS="-O2 -D_I386MACH_ALLOW_HW_INTERRUPTS -DSIGNAL_PROVIDED -mtls-use-call"
%configure \
	CFLAGS="-O2" \
	CFLAGS_FOR_TARGET="$NEWLIB_CFLAGS" \
	CXXFLAGS_FOR_TARGET="$NEWLIB_CFLAGS" \
	MAKEINFO=/bin/false \
	libc_cv_initfinit_array=yes \
	--disable-libgloss \
	--enable-newlib-iconv \
	--enable-newlib-io-long-long \
	--enable-newlib-io-long-double \
	--enable-newlib-io-c99-formats \
	--enable-newlib-mb \
	--target=%{target}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Conflicts with binutils
%{__rm} -r $RPM_BUILD_ROOT%{_infodir}

# The default pthread.h doesn't work right?
%{__rm} $RPM_BUILD_ROOT%{archincludedir}/pthread.h
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{archincludedir}

# We have to hack up libc.a to get things working.
# 32bit
%{__mv} $RPM_BUILD_ROOT%{archlibdir}/32/libc.a $RPM_BUILD_ROOT%{archlibdir}/32/libcrt_common.a
sed "s/@OBJFORMAT@/elf32-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{archlibdir}/32/libc.a

# 64bit (default)
%{__mv} $RPM_BUILD_ROOT%{archlibdir}/libc.a $RPM_BUILD_ROOT%{archlibdir}/libcrt_common.a
sed "s/@OBJFORMAT@/elf64-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{archlibdir}/libc.a

# move to match -m32 -lm search path gcc uses: /usr/x86_64-nacl/lib32/libm.a
install -d $RPM_BUILD_ROOT%{archlib32dir}
%{__mv} $RPM_BUILD_ROOT%{archlibdir}/32/* $RPM_BUILD_ROOT%{archlib32dir}
rmdir $RPM_BUILD_ROOT%{archlibdir}/32
# move -m64 objects to %{archlib64dir}?

# fix copies to be hardlinks (maybe should symlink in the future)
findup -m $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_datadir}/iconv_data
%dir %{archincludedir}
%{archincludedir}/*.h
%{archincludedir}/bits
%{archincludedir}/machine
%{archincludedir}/sys
%dir %{archlibdir}
%{archlibdir}/libc.a
%{archlibdir}/libcrt_common.a
%{archlibdir}/libg.a
%{archlibdir}/libm.a
%{archlibdir}/crt0.o
%{archlib32dir}/libc.a
%{archlib32dir}/libcrt_common.a
%{archlib32dir}/libg.a
%{archlib32dir}/libm.a
%{archlib32dir}/crt0.o
