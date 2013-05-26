%define		gitver 5feee65
Summary:	C library intended for use on embedded systems
Name:		crossnacl-newlib
Version:	1.20.0
Release:	5.git%{gitver}
License:	BSD and MIT and LGPL v2+
Group:		Libraries
Source0:	nacl-newlib-%{version}-git%{gitver}.tar.xz
# Source0-md5:	18a0d0c7058903c35f2ef5f140fd53dc
Source1:	nacl-headers-27.0.1453.93.tar.xz
# Source1-md5:	1718b8b1fb5f5354002469413352c679
Source2:	newlib-libc-script
Source3:	pthread.h
Source4:	get-source.sh
URL:		http://sourceware.org/newlib/
BuildRequires:	crossnacl-binutils
BuildRequires:	crossnacl-gcc
BuildRequires:	fslint
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		x86_64-nacl

%description
Newlib is a C library intended for use on embedded systems. It is a
conglomeration of several library parts, all under free software
licenses that make them easily usable on embedded products.

This is the NaCl fork.

%prep
%setup -q -n nacl-newlib-%{version}-git%{?gitver}
tar -xvf %{SOURCE1} -C newlib/libc/sys/nacl --strip-components=1
cp -p %{SOURCE2} .

%{__rm} etc/*.texi

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
	MAKEINFO=/bin/false \
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
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_prefix}/%{target}/include

# We have to hack up libc.a to get things working.
# 32bit
mv $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libc.a $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libcrt_common.a
sed "s/@OBJFORMAT@/elf32-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32/libc.a

# 64bit (default)
mv $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libc.a $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libcrt_common.a
sed "s/@OBJFORMAT@/elf64-nacl/" newlib-libc-script > $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/libc.a

# move to match -m32 -lm search path gcc uses: /usr/x86_64-nacl/lib32/libm.a
install -d $RPM_BUILD_ROOT%{_prefix}/%{target}/lib32
mv $RPM_BUILD_ROOT%{_prefix}/%{target}/{lib/32/*,lib32}
rmdir $RPM_BUILD_ROOT%{_prefix}/%{target}/lib/32

# fix copies to be hardlinks (maybe should symlink in the future)
findup -m $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_datadir}/iconv_data
%{_prefix}/%{target}/include
%{_prefix}/%{target}/lib
%dir %{_prefix}/%{target}/lib32
%{_prefix}/%{target}/lib32/lib*.a
%{_prefix}/%{target}/lib32/crt*.o
