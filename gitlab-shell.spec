Summary:	GitLab ssh access and repository management
Name:		gitlab-shell
Version:	2.6.12
Release:	0.6
License:	MIT
Group:		Applications/Shells
Source0:	https://github.com/gitlabhq/gitlab-shell/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	730c60e3d3d14d0f0ce0e82ff3a88a23
Patch0:		config.yml.patch
URL:		https://github.com/gitlabhq/gitlab-shell
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
Suggests:	redis
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define gitlab_uid 65434
%define gitlab_gid 65434
%define homedir %{_localstatedir}/lib/gitlab

%description
GitLab Shell is an application that allows you to execute git commands
and provide ssh access to git repositories. It is not a Unix shell nor
a replacement for Bash or Zsh.

%prep
%setup -q
%patch0 -p1

mv config.yml.example config.yml

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -a * $RPM_BUILD_ROOT%{_datadir}/%{name}

# exclude tests and other unwanted files
rm -r $RPM_BUILD_ROOT%{_datadir}/%{name}/spec
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/debug*

install -d $RPM_BUILD_ROOT%{homedir}/.ssh
touch $RPM_BUILD_ROOT%{homedir}/.ssh/authorized_keys

install -d $RPM_BUILD_ROOT%{homedir}/repositories

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
if [ $1 -ge 1 ]; then
	%groupadd gitlab -g %{gitlab_gid}
	%useradd -u %{gitlab_uid} -c 'Gitlab user' -d %{homedir} -g gitlab -s /bin/false gitlab
fi

%post
if [ $1 -eq 1 ]; then
	echo "INFO: after installing gitlab run:"
	echo "      sudo -u gitlab -H bundle exec rake gitlab:shell:setup RAILS_ENV=production"
fi

%files
%defattr(644,root,root,755)
%doc LICENSE
%dir %{_sysconfdir}/gitlab
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/gitlab-shell-config.yml
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/.gitlab_shell_secret
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/lib
%dir %{_datadir}/%{name}/bin
%attr(755,root,root) %{_datadir}/%{name}/bin/*
%{_datadir}/%{name}/.gitlab_shell_secret
%{_datadir}/%{name}/[A-Z]*
%{_datadir}/%{name}/config.yml
%dir %{_datadir}/%{name}/hooks
%attr(755,root,root) %{_datadir}/%{name}/hooks/*
%dir %{_datadir}/%{name}/support
%attr(755,root,root) %{_datadir}/%{name}/support/*

%dir %{homedir}
%dir %attr(700,gitlab,gitlab) %{homedir}/.ssh
%config(noreplace) %attr(600,gitlab,gitlab) %{homedir}/.ssh/authorized_keys
%dir %attr(2770,gitlab,gitlab) %{homedir}/repositories
