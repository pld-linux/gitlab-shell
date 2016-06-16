%define uid 264
%define gid 264
%define uname git
%define gname git
Summary:	GitLab ssh access and repository management
Name:		gitlab-shell
Version:	3.0.0
Release:	1
License:	MIT
Group:		Applications/Shells
Source0:	https://github.com/gitlabhq/gitlab-shell/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	1798d8026f92729b607d9656ca6c6c01
Patch0:		config.yml.patch
URL:		https://github.com/gitlabhq/gitlab-shell
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
BuildRequires:	sed >= 4.0
Provides:	group(%{gname})
Provides:	user(%{uname})
Conflicts:	gitlab-ce < 8.7.5-0.17
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	git-core >= 2.7.3
Requires:	ruby >= 1:2.0
Requires:	ruby-redis >= 3.3.0
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define homedir %{_localstatedir}/lib/gitlab

%description
GitLab Shell is an application that allows you to execute git commands
and provide ssh access to git repositories. It is not a Unix shell nor
a replacement for Bash or Zsh.

%prep
%setup -q
cp -p config.yml.example config.yml
%patch0 -p1

%{__sed} -i -e '1 s,#!.*ruby,#!%{__ruby},' bin/* hooks/*

# deprecated
rm support/rewrite-hooks.sh
# stupid script, rather not package it at all
rm support/truncate_repositories.sh*

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -a VERSION *.yml bin lib hooks support $RPM_BUILD_ROOT%{_datadir}/%{name}

install -d $RPM_BUILD_ROOT%{homedir}/{.ssh,repositories}
touch $RPM_BUILD_ROOT%{homedir}/.ssh/authorized_keys

install -d $RPM_BUILD_ROOT%{_sysconfdir}/gitlab
mv $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml $RPM_BUILD_ROOT%{_sysconfdir}/gitlab/gitlab-shell-config.yml
ln -sf %{_sysconfdir}/gitlab/gitlab-shell-config.yml $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml

# it will attempt to symlink if it doesn't exist
# /var/lib/gitlab/config/initializers/gitlab_shell_secret_token.rb +18
touch $RPM_BUILD_ROOT%{_sysconfdir}/gitlab/.gitlab_shell_secret
ln -s %{_sysconfdir}/gitlab/.gitlab_shell_secret $RPM_BUILD_ROOT%{_datadir}/%{name}/.gitlab_shell_secret

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g %{gid} %{gname}
%useradd -u %{uid} -c 'Git user' -d %{homedir} -g git -s /bin/false %{uname}

%post
%banner -o -e %{name} <<EOF

To rebuild authorized_keys file, run:

  # gitlab-rake gitlab:shell:setup

http://docs.gitlab.com/ce/raketasks/maintenance.html#rebuild-authorized_keys-file

EOF

%postun
if [ "$1" = "0" ]; then
	%userremove git
	%groupremove git
fi

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG LICENSE
%dir %{_sysconfdir}/gitlab
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/gitlab-shell-config.yml
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/.gitlab_shell_secret
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/lib
%dir %{_datadir}/%{name}/bin
%attr(755,root,root) %{_datadir}/%{name}/bin/*
%{_datadir}/%{name}/.gitlab_shell_secret
%{_datadir}/%{name}/config.yml
%{_datadir}/%{name}/VERSION
%dir %{_datadir}/%{name}/hooks
%attr(755,root,root) %{_datadir}/%{name}/hooks/*

%dir %{homedir}
%dir %attr(700,%{uname},%{gname}) %{homedir}/.ssh
%config(noreplace) %attr(600,%{uname},%{gname}) %{homedir}/.ssh/authorized_keys
%dir %attr(2770,%{uname},%{gname}) %{homedir}/repositories
