Summary:	GitLab ssh access and repository management
Name:		gitlab-shell
Version:	1.9.5
Release:	0.1
License:	MIT
Group:		Applications/Shells
Source0:	https://github.com/gitlabhq/gitlab-shell.git/v%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	155af9f2ad05d6e55c63737bf3497758
URL:		https://github.com/gitlabhq/gitlab-shell
Patch0:		config.yml.patch
Requires:	redis
Requires:	ruby-bundler
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
%config(noreplace) %{_sysconfdir}/gitlab/gitlab-shell-config.yml
%{_datadir}/gitlab-shell/*
%dir %attr(700,gitlab,gitlab) %{homedir}/.ssh
%config(noreplace) %attr(600,gitlab,gitlab) %{homedir}/.ssh/authorized_keys
%dir %attr(2770,gitlab,gitlab) %{homedir}/repositories
