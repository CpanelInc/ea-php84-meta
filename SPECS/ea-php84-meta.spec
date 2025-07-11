# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 84
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

Summary:       Package that installs PHP 8.4
Name:          %scl_name
Version:       8.4.10
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define        release_prefix 1
Release:       %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README.md
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli

# Our code requires that pear be installed when the meta package is installed
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 8.4 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php84/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Remove empty share/[man|locale]/ directories
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/man/ -type d -empty -delete
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale/ -type d -empty -delete
mkdir -p %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php84/root/etc
%dir /opt/cpanel/ea-php84/root/usr
%dir /opt/cpanel/ea-php84/root/usr/share
%dir /opt/cpanel/ea-php84/root/usr/share/doc
%dir /opt/cpanel/ea-php84/root/usr/include
%dir /opt/cpanel/ea-php84/root/usr/share/man
%dir /opt/cpanel/ea-php84/root/usr/bin
%dir /opt/cpanel/ea-php84/root/usr/var
%dir /opt/cpanel/ea-php84/root/usr/var/cache
%dir /opt/cpanel/ea-php84/root/usr/var/tmp
%dir /opt/cpanel/ea-php84/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Thu Jul 03 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.10-1
- EA-12995: Update ea-php84 from v8.4.8 to v8.4.10

* Thu Jun 05 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.8-1
- EA-12918: Update ea-php84 from v8.4.7 to v8.4.8

* Thu May 08 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.7-1
- EA-12851: Update ea-php84 from v8.4.6 to v8.4.7

* Thu Apr 10 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.6-1
- EA-12808: Update ea-php84 from v8.4.5 to v8.4.6

* Thu Mar 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.5-1
- EA-12768: Update ea-php84 from v8.4.4 to v8.4.5

* Thu Feb 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.4-1
- EA-12709: Update ea-php84 from v8.4.3 to v8.4.4

* Fri Jan 17 2025 Cory McIntire <cory@cpanel.net> - 8.4.3-1
- EA-12652: Update ea-php84 from v8.4.2 to v8.4.3

* Thu Dec 19 2024 Cory McIntire <cory@cpanel.net> - 8.4.2-1
- EA-12619: Update ea-php84 from v8.4.1 to v8.4.2

* Thu Nov 21 2024 Dan Muey <daniel.muey@webpros.com> - 8.4.1-1
- EA-12579: Update ea-php84 from v8.4.0 to v8.4.1

* Fri Oct 04 2024 Julian Brown <julian.brown@cpanel.net> - 8.4.0-1
- ZC-12235: First build

