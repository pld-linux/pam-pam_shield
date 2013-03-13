# TODO
# - no idea about selinux stuff in scriptlets. enable if tested and working
%define		modulename	pam_shield
Summary:	Pam Shield - A pam module to counter brute force attacks
Name:		pam-%{modulename}
Version:	0.9.5
Release:	0.1
License:	GPL v2
Group:		Libraries
URL:		http://www.heiho.net/pam_shield/index.html
Source0:	http://www.heiho.net/pam_shield/pam_shield-%{version}.tar.gz
# Source0-md5:	cbfcd96fad38943ed78fd4d37307aba2
Source1:	shield-trigger.8.gz
# Source1-md5:	df589554cb2a80dca43793e127090a0b
Source2:	shield-purge.8.gz
# Source2-md5:	88ba04e0a41db33d386b723358cc76b0
Source3:	shield-trigger-iptables.8.gz
# Source3-md5:	798818abd2b963c6c2dc6259cba4c661
BuildRequires:	gdbm-devel
BuildRequires:	pam-devel
Requires:	policycoreutils-python
Patch0:		shield_purge_segfault.patch
Patch1:		shield-trigger-iptables.patch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a pam module that supports brute force blocking against pam
authentication mechanisms.

%prep
%setup -q -n %{modulename}-%{version}
%patch0 -p0
%patch1 -p0

# disable debug by default
sed -i -e 's/debug on/debug off/' shield.conf
# change to block all users for failed attempts
sed -i -e 's/block unknown-users/block all-users/' shield.conf
# reduce connections before block from 10 to 3
sed -i -e 's/max_conns 10/max_conns 3/' shield.conf
# reduce retention time from 1 week to 1 hour
sed -i -e 's/retention 1w/retention 1h/' shield.conf
# change the default behavior from shield-trigger to shield-trigger-iptables
# this uses iptables instead of route to block brute force attack
sed -i -e 's/shield\-trigger/shield-trigger-iptables/' shield.conf

%build
# software required -fPIC flag to build
%{__make} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -fPIC"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{security,cron.daily},/%{_lib}/security,%{_sbindir},%{_mandir}/man8,/var/lib/pam_shield}
install -p pam_shield.so $RPM_BUILD_ROOT/%{_lib}/security
install -p pam_shield.cron $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/pam_shield
install -p shield-trigger $RPM_BUILD_ROOT%{_sbindir}
install -p shield-trigger-iptables $RPM_BUILD_ROOT%{_sbindir}
install -p shield-purge $RPM_BUILD_ROOT%{_sbindir}
cp -p shield.conf $RPM_BUILD_ROOT/etc/security
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{_mandir}/man8

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%post
semanage fcontext -a -t var_auth_t '/var/lib/pam_shield' 2>/dev/null || :
restorecon -R /var/lib/pam_shield || :

%postun
if [ $1 -eq 0 ]; then
	semanage fcontext -d -t var_auth_t '/var/lib/pam_shield' 2>/dev/null || :
	if [ -e "/var/lib/pam_shield/db" ]; then
		rm -f /var/lib/pam_shield/db
	fi
fi
%endif

%files
%defattr(644,root,root,755)
%doc INSTALL README CREDITS Changelog
%config(noreplace) %verify(not md5 mtime size) /etc/security/shield.conf
%attr(755,root,root) /%{_lib}/security/pam_shield.so
%attr(755,root,root) %{_sbindir}/shield-trigger
%attr(755,root,root) %{_sbindir}/shield-purge
%attr(755,root,root) %{_sbindir}/shield-trigger-iptables
%{_mandir}/man8/shield-trigger.8*
%{_mandir}/man8/shield-purge.8*
%{_mandir}/man8/shield-trigger-iptables.8*
%dir /var/lib/pam_shield
%attr(755,root,root) /etc/cron.daily/pam_shield
