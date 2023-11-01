%global _hardened_build 1

Summary: An utility for finding files by name
Name: mlocate
Version: 0.26
Release: 20%{?dist}
License: GPLv2
URL: https://fedorahosted.org/mlocate/
Group: Applications/System
Source0: https://fedorahosted.org/releases/m/l/mlocate/mlocate-%{version}.tar.xz
Source1: updatedb.conf
Source2: mlocate-run-updatedb
Source3: mlocate-updatedb.service
Source4: mlocate-updatedb.timer
Requires(pre): shadow-utils
Requires(post): grep, sed
# standard systemd requires
%{?systemd_requires}
BuildRequires: systemd
Provides: bundled(gnulib)
Obsoletes: slocate <= 2.7-30

%description
mlocate is a locate/updatedb implementation.  It keeps a database of
all existing files and allows you to lookup files by name.

The 'm' stands for "merging": updatedb reuses the existing database to avoid
rereading most of the file system, which makes updatedb faster and does not
trash the system caches as much as traditional locate implementations.

%prep
%setup -q

%build
%configure --localstatedir=%{_localstatedir}/lib
make %{?_smp_mflags} groupname=slocate

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p' groupname=slocate

mkdir -p $RPM_BUILD_ROOT{%{_sysconfdir},/etc/cron.daily}
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/updatedb.conf
install -D -p -m 750 %{SOURCE2} $RPM_BUILD_ROOT%{_libexecdir}/mlocate-run-updatedb
install -D -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}/mlocate-updatedb.service
install -D -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/mlocate-updatedb.timer

# %%ghost semantics is so stupid
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/mlocate/mlocate.db

%find_lang mlocate

%pre
getent group slocate >/dev/null || groupadd -g 21 -r -f slocate
exit 0

%post
if /bin/grep -q '^[^#]*DAILY_UPDATE' %{_sysconfdir}/updatedb.conf; then
    /bin/sed -i.rpmsave -e '/DAILY_UPDATE/s/^/#/' %{_sysconfdir}/updatedb.conf
fi
%systemd_post mlocate-updatedb.timer
systemctl start mlocate-updatedb.timer

%preun
%systemd_preun mlocate-updatedb.timer

%postun
%systemd_postun_with_restart mlocate-updatedb.timer

%triggerin -- %{name} < 0.26-11
/usr/bin/systemctl start mlocate-updatedb.timer

%files -f mlocate.lang
%doc AUTHORS COPYING NEWS README
%config(noreplace) %{_sysconfdir}/updatedb.conf
%attr(2711,root,slocate) %{_bindir}/locate
%{_unitdir}/mlocate-updatedb.service
%{_unitdir}/mlocate-updatedb.timer
%{_libexecdir}/mlocate-run-updatedb
%{_bindir}/updatedb
%{_mandir}/man*/*
%dir %attr(0750,root,slocate) %{_localstatedir}/lib/mlocate
%ghost %attr(0640,root,slocate) %{_localstatedir}/lib/mlocate/mlocate.db

%changelog
* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.26-20
- Escape macros in %%changelog

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.26-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.26-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.26-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.26-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Sep 13 2016 Adam Williamson <awilliam@redhat.com> - 0.26-15
- add correct systemd requirements for scriptlets (using %%systemd_requires)

* Fri Mar 18 2016 Michal Sekletar <msekleta@redhat.com> - 0.26-14
- start timer after the installation (#1278587)
- make mlocate-updatedb.service of the type simple, systemd will then not wait for its completion (#1282232)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.26-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun  9 2015 Michal Sekletar <msekleta@redhat.com> - 0.26-11
- migrate from cron job to systemd timer
- prune ceph filesystem (#1223582)

* Tue May 26 2015 Michal Sekletar <msekleta@redhat.com> - 0.26-10
- prune path /var/lib/ceph (#1223582)

* Mon Jan 26 2015 Michal Sekletar <msekleta@redhat.com> - 0.26-9
- mlocate.db is ghost file created with non-default attrs, list them explicitly so rpm --verify doesn't report errors

* Wed Jan  7 2015 Michal Sekletar <msekleta@redhat.com> - 0.26-8
- change permissions of cron script to conform with Red Hat Security Guide (#1179721)
- prune meta-data dirs of couple more VCS systems (#949320)
- prune dnf db dir, same as we do for yum (#1177877)
- add gpfs to PRUNEFS (#1179644)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jul 25 2014 Michal Sekletar <msekleta@redhat.com> - 0.26-6
- Don't add zfs to PRUNEFS when calling updatedb from cron (#1065366)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Apr 10 2013 Miloslav Trmač <mitr@redhat.com> - 0.26-3
- Update cron packaging for https://fedoraproject.org/wiki/Packaging:CronFiles
  Notably, the cron script (previously not %%config) was renamed.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Sep 22 2012 Miloslav Trmač <mitr@redhat.com> - 0.26-1
- Update to mlocate-0.26
- Drop no longer necessary %%clean and %%defattr commands.
- Enable hardened build
  Resolves: #853189

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Mar  3 2012 Miloslav Trmač <mitr@redhat.com> - 0.25-1
- Update to mlocate-0.25
- Add /var/lib/yum/yumdb to PRUNEPATHS
  Resolves: #747918

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Mar 31 2011 Miloslav Trmač <mitr@redhat.com> - 0.24-1
- Update to mlocate-0.24
  Resolves: #675189
- Explicitly exclude fuse.sshfs.  Ideally we'd like to exclude all fuse.* file
  systems, sshfs is urgent because it it can hang updatedb.
  Resolves: #604145, #608094

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.23.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb  4 2011 Miloslav Trmač <mitr@redhat.com> - 0.23.1-4
- Add Provides: bundled(gnulib)

* Fri Feb  4 2011 Miloslav Trmač <mitr@redhat.com> - 0.23.1-3
- Exclude /mnt by default
  Resolves: #674635
- Drop %%triggerpostun on slocate - it is long obsolete, and rpm started
  rejecting "Requries(triggerpostun)"

* Wed Sep 29 2010 jkeating - 0.23.1-2
- Rebuilt for gcc bug 634757

* Tue Sep 14 2010 Miloslav Trmač <mitr@redhat.com> - 0.23.1-1
- Update to mlocate-0.23.1

* Thu Aug 26 2010 Miloslav Trmač <mitr@redhat.com> - 0.23-1
- Update to mlocate-0.23
- Don't exclude rootfs, to avoid ambiguity when handling "/"
  Resolves: #624551

* Tue Mar 30 2010 Miloslav Trmač <mitr@redhat.com> - 0.22.4-2
- Ignore no-op bind mounts
  Resolves: #577819

* Fri Mar 26 2010 Miloslav Trmač <mitr@redhat.com> - 0.22.4-1
- Update to mlocate-0.22.4

* Thu Mar  4 2010 Miloslav Trmač <mitr@redhat.com> - 0.22.3-1
- Update to mlocate-0.22.3
- Remove no longer necessary references to BuildRoot:

* Fri Jan 15 2010 Miloslav Trmač <mitr@redhat.com> - 0.22.2-2
- Add "lustre" to PRUNEFS
- Add all nodev filesystems from the Fedora kernel to PRUNEFS, to make
  (updatedb) work as some users expect

* Fri Oct  2 2009 Miloslav Trmač <mitr@redhat.com> - 0.22.2-1
- Update to mlocate-0.22.2

* Tue Sep 15 2009 Miloslav Trmač <mitr@redhat.com> - 0.22.1-1
- Update to mlocate-0.22.1
- Drop Provides: slocate, per NamingGuidelines

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.22-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 19 2009 Miloslav Trmač <mitr@redhat.com> - 0.22-2
- Add /var/cache/ccache to PRUNEPATHS.

* Tue Apr 14 2009 Miloslav Trmač <mitr@redhat.com> - 0.22-1
- Update to mlocate-0.22

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 12 2009 Miloslav Trmač <mitr@redhat.com> - 0.21.1-3
- Merge review fixes, based on a patch by Parag AN:
  - Use %%{_localstatedir}/lib instead of hard-coding /var/lib
  - Use %%{?_smp_mflags}
  - Preserve file time stamps
  - Only create the group if it doesn't exist, hide errors from rpm

* Fri Nov 28 2008 Miloslav Trmač <mitr@redhat.com> - 0.21.1-2
- Add .git to PRUNENAMES
  Resolves: #473227
- Avoid a rpmlint warning

* Tue Oct 28 2008 Miloslav Trmač <mitr@redhat.com> - 0.21.1-1
- Update to mlocate-0.21
  Resolves: #461208

* Mon Jun 30 2008 Miloslav Trmač <mitr@redhat.com> - 0.21-1
- Update to mlocate-0.21
- Define PRUNENAMES to exclude .svn and .hg

* Wed Apr  9 2008 Miloslav Trmač <mitr@redhat.com> - 0.20-1
- Update to mlocate-0.20

* Mon Mar  3 2008 Miloslav Trmač <mitr@redhat.com> - 0.19-1
- Update to mlocate-0.19
- New home page at https://fedorahosted.org/mlocate/ .

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.18-2
- Autorebuild for GCC 4.3

* Sat Aug 25 2007 Miloslav Trmač <mitr@redhat.com> - 0.18-1
- Update to mlocate-0.18
- Run updatedb with reduced I/O priority
  Resolves: #254165

* Wed Apr 25 2007 Miloslav Trmac <mitr@redhat.com> - 0.17-1
- Update to mlocate-0.17
  Resolves: #237120

* Tue Mar  6 2007 Miloslav Trmac <mitr@redhat.com> - 0.16-1
- Update to mlocate-0.16
- Enable PRUNE_BIND_MOUNTS by default
  Resolves: #221755

* Fri Jan  5 2007 Miloslav Trmac <mitr@redhat.com> - 0.15-2
- Add gfs and gfs2 to PRUNEFS
  Resolves: #220491

* Thu Nov 16 2006 Miloslav Trmac <mitr@redhat.com> - 0.15-1
- Update to mlocate-0.15
  Resolves: #215763

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.14-2.1
- rebuild

* Sat Mar 18 2006 Miloslav Trmac <mitr@redhat.com> - 0.14-2
- Ship NEWS

* Sat Mar 18 2006 Miloslav Trmac <mitr@redhat.com> - 0.14-1
- Update to mlocate-0.14

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.12-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.12-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sat Dec 31 2005 Miloslav Trmac <mitr@redhat.com> - 0.12-1
- Update to mlocate-0.12

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Dec  2 2005 Miloslav Trmac <mitr@redhat.com> - 0.11-2
- Comment out DAILY_UPDATE from updatedb.conf (#174693)

* Thu Nov 10 2005 Miloslav Trmac <mitr@redhat.com> - 0.11-1
- Update to mlocate-0.11
- Add scriptlets to create group slocate

* Thu Jul 28 2005 Miloslav Trmac <mitr@volny.cz> - 0.10-0.testing.1
- Update to mlocate-0.10

* Thu Jul 28 2005 Miloslav Trmac <mitr@volny.cz> - 0.09-0.testing.1
- Initial build.
