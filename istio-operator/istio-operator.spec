# Generate devel rpm
%global with_devel 0
# Build with debug info rpm
%global with_debug 0
# Run unit tests
%global with_tests 0
# Build test binaries
%global with_test_binaries 0

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global git_commit af322b2a80d4f191e899be74387b3745f6ebcc31
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            istio-operator

# charts
%global charts_git_commit 7b77ae81a3f95cf0d0b7d30bbcacc8d151786d2d
%global chargs_git_shortcommit  %(c=%{charts_git_commit}; echo ${c:0:7})

%global charts_repo      istio
%global charts_version   1.1.0

# are we building community or product rpms
%global community_build  true

# https://github.com/maistra/istio-operator
%global provider_prefix %{provider}.%{provider_tld}/%{project}

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio-operator
Version:        0.12.0
Release:        2%{?dist}
Summary:        A Kubernetes operator to manage Istio.
License:        ASL 2.0
URL:            https://%{provider_prefix}/%{repo}

Source0:        https://%{provider_prefix}/%{repo}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz
Source1:        https://%{provider_prefix}/%{charts_repo}/archive/%{charts_git_commit}/%{charts_repo}-%{charts_git_commit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  golang >= 1.9

%description
Istio-operator is a kubernetes operator to manage the lifecycle of Istio.

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%description devel
Istio-operator is a kubernetes operator to manage the lifecycle of Istio.
%endif

%prep

rm -rf OPERATOR

mkdir -p OPERATOR/src/github.com/maistra/istio-operator
tar zxf %{SOURCE0} -C OPERATOR/src/github.com/maistra/istio-operator --strip=1

mkdir -p OPERATOR/src/github.com/maistra/istio
tar zxf %{SOURCE1} -C OPERATOR/src/github.com/maistra/istio --strip=1

%build
cd OPERATOR
export GOPATH=$(pwd):%{gopath}
pushd src/github.com/maistra/istio-operator/
./tmp/build/build.sh

popd
cp -r src/github.com/maistra/istio/install/kubernetes/helm/ src/github.com/maistra/istio-operator/tmp/_output
pushd src/github.com/maistra/istio-operator/
COMMUNITY=%{community_build} MAISTRA_VERSION=%{version} SOURCE_DIR=. HELM_DIR=./tmp/_output/helm ./tmp/build/patch-charts.sh

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}
pushd OPERATOR/src/github.com/maistra/istio-operator/tmp/_output/bin/

%if 0%{?with_debug}
    cp -pav istio-operator $RPM_BUILD_ROOT%{_bindir}/
%else
    mkdir stripped
    strip -o stripped/istio-operator -s istio-operator
    cp -pav stripped/istio-operator $RPM_BUILD_ROOT%{_bindir}/
%endif
popd

# install the charts
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/istio-operator/%{charts_version}
pushd OPERATOR/src/github.com/maistra/istio-operator/tmp/_output/
cp -rpav helm/ $RPM_BUILD_ROOT%{_sysconfdir}/istio-operator/%{charts_version}


%files
%{_bindir}/istio-operator
%{_sysconfdir}/istio-operator

%changelog
* Wed Jun 12 2019 Brian Avery <bavery@redhat.com> - 0.12.0-1
- Update to Istio 1.1.8
* Mon May 27 2019 Kevin Conner <kconner@redhat.com> - 0.11.0-6
* Pull in latest operator changes

* Fri May 24 2019 Kevin Conner <kconner@redhat.com> - 0.11.0-5
* Pull in latest operator changes

* Thu May 23 2019 Kevin Conner <kconner@redhat.com> - 0.11.0-4
* Pull in latest operator changes

* Wed May 22 2019 Brian Avery <bavery@redhat.com> - 0.11.0-3
* Move Jaeger earlier in the installation process

* Tue May 21 2019 Brian Avery <bavery@redhat.com> - 0.11.0-2
- Update Kiali version

* Mon May 20 2019 Brian Avery <bavery@redhat.com> - 0.11.0-1
- Maistra 0.11

* Thu Apr 15 2019 Rob Cernich <rcernich@redhat.com> - 0.10.0-6
- watch istio-system for ControlPlane CR
- watch istio-operator for Installation CR

* Thu Mar 28 2019 Rob Cernich <rcernich@redhat.com> - 0.10.0-1
- Added helm charts used by new installer

* Mon Mar 25 2019 Brian Avery <bavery@redhat.com> - 0.10.0-1
- Updated to 0.10.0/New installer

* Mon Mar 4 2019 Kevin Conner <kconner@redhat.com> - 0.9.0-1
- Updated to 0.9.0

* Thu Feb 14 2019 Kevin Conner <kconner@redhat.com> - 0.8.0-1
- Updated to 0.8.0

* Mon Jan 28 2019 Kevin Conner <kconner@redhat.com> - 0.7.0-3
- Updates to 3scale adapter integration

* Fri Jan 25 2019 Kevin Conner <kconner@redhat.com> - 0.7.0-2
- Updated to include 3scale adapter configuration

* Thu Jan 17 2019 Kevin Conner <kconner@redhat.com> - 0.7.0
- Updated to 0.7.0

* Thu Dec 20 2018 Kevin Conner <kconner@redhat.com> - 0.6.0
- Updated to 0.6.0

* Fri Nov 23 2018 Kevin Conner <kconner@redhat.com> - 0.5.0
- Updated to 0.5.0

* Wed Oct 31 2018 Kevin Conner <kconner@redhat.com> - 0.4.0
- Updated to 0.4.0

* Wed Oct 17 2018 Kevin Conner <kconner@redhat.com> - 0.3.0
- Updated to 0.3.0

* Fri Oct 12 2018 Brian Avery <bavery@redhat.com> - 0.3.0
- Added 0.3.0

* Tue Sep 4 2018 Brian Avery <bavery@redhat.com> - 0.1.0
- Stripped binaries

* Tue Aug 14 2018 Brian Avery <bavery@redhat.com> - 0.1.0
- First package
