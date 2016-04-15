Summary:	GitLab ssh access and repository management
Name:		gitlab-shell
Version:	2.6.12
Release:	0.3
License:	MIT
Group:		Applications/Shells
Source0:	https://github.com/gitlabhq/gitlab-shell/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	730c60e3d3d14d0f0ce0e82ff3a88a23
URL:		https://github.com/gitlabhq/gitlab-shell
Patch0:		config.yml.patch
Suggests:	redis
#Requires:	ruby-bundler
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

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/gitlab-shell
cp -a * $RPM_BUILD_ROOT%{_datadir}/gitlab-shell

install -d $RPM_BUILD_ROOT%{homedir}/.ssh
touch $RPM_BUILD_ROOT%{homedir}/.ssh/authorized_keys

install -d $RPM_BUILD_ROOT%{homedir}/repositories

install -d $RPM_BUILD_ROOT%{_sysconfdir}/gitlab
mv $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml $RPM_BUILD_ROOT%{_sysconfdir}/gitlab/gitlab-shell-config.yml
ln -sf %{_sysconfdir}/gitlab/gitlab-shell-config.yml $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml

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
%dir %{_datadir}/gitlab-shell
%dir %{_sysconfdir}/gitlab
%config(noreplace) %{_sysconfdir}/gitlab/gitlab-shell-config.yml
%{_datadir}/gitlab-shell/*
%dir %{homedir}
%dir %attr(700,gitlab,gitlab) %{homedir}/.ssh
%config(noreplace) %attr(600,gitlab,gitlab) %{homedir}/.ssh/authorized_keys
%dir %attr(2770,gitlab,gitlab) %{homedir}/repositories
