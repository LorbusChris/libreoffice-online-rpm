Name:           libreoffice-online
Version:        6.0.0.3
Release:        2%{?dist}
Summary:        LibreOffice Online Web Socket Daemon
License:        MPL

Source0:        https://github.com/LibreOffice/online/archive/libreoffice-%{version}.tar.gz
# https://gerrit.libreoffice.org/#/c/49097/
Patch0:         %{name}-no_setcap_build.patch

%{?systemd_requires}
BuildRequires:  systemd
BuildRequires:  libcap libcap-devel libpng-devel poco-devel >= 1.7.5 python python-polib pcre-devel
BuildRequires:  kernel-headers glibc-devel autoconf automake libtool cppunit-devel npm jake fontconfig

Requires(pre):  shadow-utils
Requires:       libreoffice-core systemd
Requires:       expat keyutils-libs krb5-libs libattr libcap libcom_err libgcc libpng libselinux pcre xz-libs zlib cppunit openssl-libs
Requires:       poco-crypto >= 1.7.5 poco-foundation >= 1.7.5 poco-json >= 1.7.5 poco-net >= 1.7.5 poco-netssl >= 1.7.5 poco-util >= 1.7.5 poco-xml >= 1.7.5
Requires:       atk avahi-glib avahi-libs bzip2-libs cairo cups-libs dbus-glib dbus-libs fontconfig freetype GConf2 gdk-pixbuf2 glib2 gnome-vfs2 graphite2
Requires:       gstreamer gstreamer-plugins-base gtk2 harfbuzz libdrm libffi libICE libSM libuuid libX11 libXau libxcb
Requires:       libXcomposite libXcursor libXdamage libXext libXfixes libXi libXinerama libXrandr libXrender libxshmfence libXt libXxf86vm
Requires:       mesa-libEGL mesa-libgbm mesa-libGL mesa-libglapi pango pixman python3
Requires(post): coreutils grep sed fontconfig

Provides:       loolwsd = %{version}
Obsoletes:      loolwsd <= %{version}
Provides:       loleaflet = 1.5.8
Obsoletes:      loleaflet <= 1.5.8

%description
LibreOffice Online Web Socket Daemon

%prep
%setup -n online-libreoffice-%{version}
%patch0 -p1

%build
./autogen.sh
%configure \
  --enable-silent-rules \
  --with-lokit-path=`pwd`/bundled/include \
  --with-lo-path=%{_libdir} \
  --disable-setcap

make CXXFLAGS="%{optflags} -Wno-error" %{?_smp_mflags}

%check
#make check

%install
make install DESTDIR=%{buildroot}
install -D -m 444 loolwsd.service %{buildroot}%{_unitdir}/loolwsd.service
install -d -m 755 %{buildroot}%{_localstatedir}/adm/fillup-templates
install -D -m 644 sysconfig.loolwsd %{buildroot}%{_sysconfdir}/sysconfig/loolwsd
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
cat > %{buildroot}%{_sysconfdir}/cron.d/loolwsd.cron <<EOF
#Remove old tiles once every 10 days at midnight
0 0 */1 * * root find /var/cache/loolwsd -name \"*.png\" -a -atime +10 -exec rm {} \;
EOF
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
cat > %{buildroot}%{_sysconfdir}/pam.d/loolwsd <<EOF
auth       required     pam_unix.so
account    required     pam_unix.so
EOF

%files
%{_bindir}/loolwsd
%{_bindir}/loolwsd-systemplate-setup
%{_bindir}/loolmap
%{_bindir}/loolforkit
%{_bindir}/loolmount
%{_bindir}/loolstress
%{_bindir}/looltool
%{_bindir}/loolconfig
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/favicon.ico
%{_datadir}/%{name}/discovery.xml
%{_datadir}/%{name}/robots.txt
%dir %{_datadir}/%{name}/loleaflet
%{_datadir}/%{name}/loleaflet/*
%{_unitdir}/loolwsd.service
%config(noreplace) %{_sysconfdir}/sysconfig/loolwsd
%config(noreplace) %{_sysconfdir}/cron.d/loolwsd.cron
%config(noreplace) %{_sysconfdir}/pam.d/loolwsd
%dir %{_sysconfdir}/%{name}
%config(noreplace) %attr(640, lool, root) %{_sysconfdir}/%{name}/loolwsd.xml
%config %{_sysconfdir}/%{name}/loolkitconfig.xcu
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/README.vars
%doc %{_docdir}/%{name}/protocol.txt
%doc %{_docdir}/%{name}/reference.txt
%doc README
%license COPYING

%pre
getent group lool >/dev/null || groupadd -r lool
getent passwd lool >/dev/null || useradd -g lool -r lool
exit 0

%post
setcap cap_fowner,cap_mknod,cap_sys_chroot=ep %{_bindir}/loolforkit
setcap cap_sys_admin=ep %{_bindir}/loolmount

mkdir -p %%{_localstatedir}/cache/loolwsd && chown lool:lool %{_localstatedir}/cache/loolwsd
rm -rf %{_localstatedir}/cache/loolwsd/*

# Figure out where LO is installed, let's hope it is not a mount point
# Create a directory for loolwsd on the same file system
loroot=%{_libdir}
loolparent=`cd ${loroot} && cd .. && /bin/pwd`

rm -rf ${loolparent}/lool
mkdir -p ${loolparent}/lool/child-roots
chown lool:lool ${loolparent}/lool
chown lool:lool ${loolparent}/lool/child-roots

fc-cache ${loroot}/share/fonts/truetype
su lool -c "loolwsd-systemplate-setup ${loolparent}/lool/systemplate ${loroot} >/dev/null 2>&1"

%systemd_post loolwsd.service

%preun
%systemd_preun loolwsd.service

%postun
%systemd_postun loolwsd.service

%changelog
* Sun May 13 2018 Bugzy Little <bugzylittle@gmail.com> - 6.0.0.3-2
- Reduce package install requirements

* Thu Feb 1 2018 Christian Glombek <christian.glombek@rwth-aachen.de> - 6.0.0.3-1
- Updates to version 6.0.0.3
- Adds patch to to build without env
- Adds PAM support (upstream @Timar)

* Wed Sep 27 2017 Christian Glombek <christian.glombek@rwth-aachen.de> - 5.4.2.2-1
- RPM packaging for LibreOffice Online in Fedora
- Forked from https://github.com/LibreOffice/online/blob/fdec71ad6963bd91fa56b379bdb0380776efd93a/loolwsd.spec.in
- Renamed package from loolwsd to libreoffice-online

* Mon Aug 03 2015 Mihai Varga
- added the cronjob

* Tue May 19 2015 Tor Lillqvist
- Initial RPM release
