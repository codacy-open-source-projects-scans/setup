Summary: A set of system configuration and setup files
Name: setup
Version: 2.14.6
Release: %autorelease
License: LicenseRef-Fedora-Public-Domain
Group: System Environment/Base
URL: https://pagure.io/setup/
Source0: https://releases.pagure.org/%{name}/%{name}-%{version}.tar.gz
BuildArch: noarch
#systemd-rpm-macros: required to use _tmpfilesdir macro
# https://fedoraproject.org/wiki/Changes/Remove_make_from_BuildRoot
BuildRequires: make
BuildRequires: bash tcsh perl-interpreter systemd-rpm-macros
#require system release for saner dependency order
Requires: system-release

%description
The setup package contains a set of important system configuration and
setup files, such as passwd, group, and profile.

%prep
%setup -q
./generate-sysusers-fragments.sh
./shadowconvert.sh

%build

%check
# Run any sanity checks.
make check

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
cp -ar * %{buildroot}/etc
mkdir -p %(dirname %{buildroot}%{_sysusersdir})
mv %{buildroot}/etc/sysusers.d %{buildroot}%{_sysusersdir}
mkdir -p %{buildroot}/etc/profile.d
mv %{buildroot}/etc/lang* %{buildroot}/etc/profile.d/
rm -f %{buildroot}/etc/uidgid
rm -f %{buildroot}/etc/COPYING
mkdir -p %{buildroot}/var/log
touch %{buildroot}/etc/environment
chmod 0644 %{buildroot}/etc/environment
chmod 0400 %{buildroot}/etc/{shadow,gshadow}
touch %{buildroot}/etc/fstab
echo "#Add any required envvar overrides to this file, it is sourced from /etc/profile" >%{buildroot}/etc/profile.d/sh.local
echo "#Add any required envvar overrides to this file, is sourced from /etc/csh.login" >%{buildroot}/etc/profile.d/csh.local
mkdir -p %{buildroot}/etc/motd.d
mkdir -p %{buildroot}/run/motd.d
mkdir -p %{buildroot}/usr/lib/motd.d
touch %{buildroot}/usr/lib/motd
#tmpfiles needed for files in /run
mkdir -p %{buildroot}%{_tmpfilesdir}
echo "f /run/motd 0644 root root -" >%{buildroot}%{_tmpfilesdir}/%{name}.conf
echo "d /run/motd.d 0755 root root -" >>%{buildroot}%{_tmpfilesdir}/%{name}.conf
chmod 0644 %{buildroot}%{_tmpfilesdir}/%{name}.conf

# remove unpackaged files from the buildroot
rm -f %{buildroot}/etc/Makefile
rm -f %{buildroot}/etc/serviceslint
rm -f %{buildroot}/etc/uidgidlint
rm -f %{buildroot}/etc/generate-sysusers-fragments.sh
rm -f %{buildroot}/etc/shadowconvert.sh
rm -f %{buildroot}/etc/setup.spec
rm -rf %{buildroot}/etc/contrib

# make setup a protected package
install -p -d -m 755 %{buildroot}/etc/dnf/protected.d/
touch %{name}.conf
echo setup > %{name}.conf
install -p -c -m 0644 %{name}.conf %{buildroot}/etc/dnf/protected.d/
rm -f %{name}.conf

#throw away useless and dangerous update stuff until rpm will be able to
#handle it ( http://rpm.org/ticket/6 )
%post -p <lua>
for i, name in ipairs({"passwd", "shadow", "group", "gshadow"}) do
   os.remove("/etc/"..name..".rpmnew")
end
if posix.access("/usr/bin/newaliases", "x") then
  local pid = posix.fork()
  if pid == 0 then
    posix.redirect2null(1)
    posix.exec("/usr/bin/newaliases")
  elseif pid > 0 then
    posix.wait(pid)
  end
end

%files
%license COPYING
%doc uidgid
%verify(not md5 size mtime) %config(noreplace) /etc/passwd
%verify(not md5 size mtime) %config(noreplace) /etc/group
%verify(not md5 size mtime) %attr(0000,root,root) %config(noreplace,missingok) /etc/shadow
%verify(not md5 size mtime) %attr(0000,root,root) %config(noreplace,missingok) /etc/gshadow
%verify(not md5 size mtime) %config(noreplace) /etc/subuid
%verify(not md5 size mtime) %config(noreplace) /etc/subgid
%config(noreplace) /etc/services
%verify(not md5 size mtime) %config(noreplace) /etc/exports
%config(noreplace) /etc/aliases
%config(noreplace) /etc/environment
%config(noreplace) /etc/filesystems
%config(noreplace) /etc/host.conf
%verify(not md5 size mtime) %config(noreplace) /etc/hosts
%verify(not md5 size mtime) %config(noreplace) /etc/motd
%dir /etc/motd.d
%ghost %verify(not md5 size mtime) %attr(0644,root,root) /run/motd
%dir /run/motd.d
%verify(not md5 size mtime) %config(noreplace) /usr/lib/motd
%dir /usr/lib/motd.d
%config(noreplace) /etc/printcap
%verify(not md5 size mtime) %config(noreplace) /etc/inputrc
%config(noreplace) /etc/bashrc
%config(noreplace) /etc/profile
%config(noreplace) /etc/protocols
%config(noreplace) /etc/ethertypes
%config(noreplace) /etc/csh.login
%config(noreplace) /etc/csh.cshrc
%config(noreplace) /etc/networks
%dir /etc/profile.d
%config(noreplace) /etc/profile.d/sh.local
%config(noreplace) /etc/profile.d/csh.local
/etc/profile.d/lang.{sh,csh}
%config(noreplace) %verify(not md5 size mtime) /etc/shells
%ghost %verify(not md5 size mtime) %config(noreplace,missingok) /etc/fstab
%{_tmpfilesdir}/%{name}.conf
%{_sysusersdir}/20-setup-groups.conf
%{_sysusersdir}/20-setup-users.conf
/etc/dnf/protected.d/%{name}.conf

%changelog
%autochangelog
