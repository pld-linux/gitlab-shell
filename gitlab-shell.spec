Summary:	GitLab ssh access and repository management
Name:		gitlab-shell
Version:	5.11.0
Release:	1
License:	MIT
Group:		Applications/Shells
Source0:	https://gitlab.com/gitlab-org/gitlab-shell/repository/archive.tar.bz2?ref=v%{version}&/%{name}-%{version}.tar.bz2
# Source0-md5:	275faae9b75785f595aed87c8eb3a577
Patch0:		unvendor-redis.patch
Patch1:		skip_hooks_setup.patch
Patch2:		config.yml.patch
URL:		https://gitlab.com/gitlab-org/gitlab-shell
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
BuildRequires:	sed >= 4.0
Requires:	git-core >= 2.7.3
Requires:	gitlab-common >= 8.12
Requires:	rsync
Requires:	ruby >= 1:2.0
Requires:	ruby-redis >= 3.3.0
Suggests:	redis-server
Conflicts:	gitlab-ce < 8.7.5-0.17
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
GitLab Shell is an application that allows you to execute git commands
and provide ssh access to git repositories. It is not a Unix shell nor
a replacement for Bash or Zsh.

%prep
%setup -qc
mv %{name}-*/* .
%patch -P0 -p1
%patch -P1 -p1
cp -p config.yml.example config.yml
%patch -P2 -p1

%{__sed} -i -e '1 s,#!.*ruby,#!%{__ruby},' bin/* hooks/*

mv lib/vendor .

# add hook dirs
# https://gitlab.com/gitlab-org/gitlab-shell/merge_requests/93
install -d hooks/{post-receive,pre-receive,update}.d

# deprecated
rm support/rewrite-hooks.sh
# stupid script, rather not package it at all
rm support/truncate_repositories.sh*

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -a VERSION *.yml bin lib hooks $RPM_BUILD_ROOT%{_datadir}/%{name}

install -d $RPM_BUILD_ROOT%{_sysconfdir}/gitlab
mv $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml $RPM_BUILD_ROOT%{_sysconfdir}/gitlab/gitlab-shell-config.yml
ln -sf %{_sysconfdir}/gitlab/gitlab-shell-config.yml $RPM_BUILD_ROOT%{_datadir}/gitlab-shell/config.yml

# it will attempt to symlink if it doesn't exist
# /var/lib/gitlab/config/initializers/gitlab_shell_secret_token.rb +18
touch $RPM_BUILD_ROOT%{_sysconfdir}/gitlab/.gitlab_shell_secret
ln -s %{_sysconfdir}/gitlab/.gitlab_shell_secret $RPM_BUILD_ROOT%{_datadir}/%{name}/.gitlab_shell_secret

%clean
rm -rf $RPM_BUILD_ROOT

%post
%banner -o -e %{name} <<EOF

To rebuild authorized_keys file, run:

  # gitlab-rake gitlab:shell:setup

http://docs.gitlab.com/ce/raketasks/maintenance.html#rebuild-authorized_keys-file

EOF

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG LICENSE
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/gitlab-shell-config.yml
%attr(640,git,git) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gitlab/.gitlab_shell_secret
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/lib
%dir %{_datadir}/%{name}/bin
%attr(755,root,root) %{_datadir}/%{name}/bin/*
%{_datadir}/%{name}/.gitlab_shell_secret
%{_datadir}/%{name}/config.yml
%{_datadir}/%{name}/VERSION

%dir %{_datadir}/%{name}/hooks
%dir %{_datadir}/%{name}/hooks/post-receive.d
%dir %{_datadir}/%{name}/hooks/pre-receive.d
%dir %{_datadir}/%{name}/hooks/update.d
%attr(755,root,root) %{_datadir}/%{name}/hooks/post-receive
%attr(755,root,root) %{_datadir}/%{name}/hooks/pre-receive
%attr(755,root,root) %{_datadir}/%{name}/hooks/update
