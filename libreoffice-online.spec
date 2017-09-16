%define build_timestamp %(date +"%Y%m%d%H%M%%S")

Name:           libreoffice-online
Version:        canary
Release:        %{build_timestamp}%{?dist}
Vendor:         %{vendor}
Summary:        LibreOffice Online Web Services Daemon
License:        MPL

Source0:        https://github.com/LorbusChris/online/archive/master.tar.gz

BuildRequires:  libcap libcap-devel libpng-devel poco-devel >= 1.7.5 python python-polib systemd
BuildRequires:  kernel-headers glibc-devel autoconf automake libtool cppunit-devel npm jake fontconfig

Requires:       libreoffice systemd
Requires:       expat keyutils-libs krb5-libs libattr libcap libcom_err libgcc libpng libselinux pcre xz-libs zlib cppunit openssl-libs
Requires:       poco-crypto >= 1.7.5 poco-foundation >= 1.7.5 poco-json >= 1.7.5 poco-net >= 1.7.5 poco-netssl >= 1.7.5 poco-util >= 1.7.5 poco-xml >= 1.7.5
Requires:       atk avahi-glib avahi-libs bzip2-libs cairo cups-libs dbus-glib dbus-libs fontconfig freetype GConf2 gdk-pixbuf2 glib2 gnome-vfs2 graphite2 gstreamer gstreamer-plugins-base gtk2 harfbuzz libdrm libffi libICE libSM libuuid libX11 libXau libxcb libXcomposite libXcursor libXdamage libXext libXfixes libXi libXinerama libXrandr libXrender libxshmfence libXt libXxf86vm mesa-libEGL mesa-libgbm mesa-libGL mesa-libglapi pango pixman python3
Requires(post): coreutils grep sed fontconfig

Provides:       loleaflet = 1.5.8
Obsoletes:      loleaflet <= 1.5.8

%description

%prep
%setup -n online-master

%build
./autogen.sh
%configure \
  --enable-silent-rules \
  --with-lokit-path=`pwd`/bundled/include \
  --with-lo-path=%{_libdir}

env BUILDING_FROM_RPMBUILD=yes make CXXFLAGS="%{optflags} -Wno-error" %{?_smp_mflags}

%check
#env BUILDING_FROM_RPMBUILD=yes make check

%install
env BUILDING_FROM_RPMBUILD=yes make install DESTDIR=%{buildroot}
%__install -D -m 444 loolwsd.service %{buildroot}%{_unitdir}/loolwsd.service
install -d -m 755 %{buildroot}/var/adm/fillup-templates
install -D -m 644 sysconfig.loolwsd %{buildroot}/etc/sysconfig/loolwsd
mkdir -p %{buildroot}/etc/cron.d
echo "#Remove old tiles once every 10 days at midnight" > %{buildroot}/etc/cron.d/loolwsd.cron
echo "0 0 */1 * * root find /var/cache/loolwsd -name \"*.png\" -a -atime +10 -exec rm {} \;" >> %{buildroot}/etc/cron.d/loolwsd.cron

%files
/usr/bin/loolwsd
/usr/bin/loolwsd-systemplate-setup
/usr/bin/loolmap
/usr/bin/loolforkit
/usr/bin/loolmount
/usr/bin/loolstress
/usr/bin/looltool
/usr/bin/loolconfig
/usr/share/loolwsd/discovery.xml
/usr/share/loolwsd/favicon.ico
/usr/share/loolwsd/robots.txt
/usr/share/loolwsd/loleaflet
/usr/share/doc/loolwsd/README
/usr/share/doc/loolwsd/README.vars
/usr/share/doc/loolwsd/protocol.txt
/usr/share/doc/loolwsd/reference.txt
%{_unitdir}/loolwsd.service
%config(noreplace) /etc/sysconfig/loolwsd
%config(noreplace) /etc/cron.d/loolwsd.cron
%config(noreplace) %attr(640, lool, root) /etc/loolwsd/loolwsd.xml
%config /etc/loolwsd/loolkitconfig.xcu

%doc README

%pre
getent group lool >/dev/null || groupadd -r lool
getent passwd lool >/dev/null || useradd -g lool -r lool

%post
setcap cap_fowner,cap_mknod,cap_sys_chroot=ep /usr/bin/loolforkit
setcap cap_sys_admin=ep /usr/bin/loolmount

mkdir -p /var/cache/loolwsd && chown lool:lool /var/cache/loolwsd
rm -rf /var/cache/loolwsd/*

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
* Sat Sep 16 2017 Christian Glombek <christian.glombek@rwth-aachen.de> canary-20170916130038
- libreoffice-online package built with tito

* Sun Aug 06 2017 Christian Glombek <christian.glombek@rwth-aachen.de> 5.4.0.2
- RPM packaging for LibreOffice Online in Fedora
- Forked from https://github.com/LibreOffice/online/blob/fdec71ad6963bd91fa56b379bdb0380776efd93a/loolwsd.spec.in
* Mon Aug 03 2015 Mihai Varga
- added the cronjob
* Tue May 19 2015 Tor Lillqvist
- Initial RPM release
