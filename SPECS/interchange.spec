# To do:
# Deal with broken UI image location
# Check for existing foundation catalog before install (can't count on RPM checks)
# Adapt foundation uninstall for new makecat method
# Use new install stuff in foundation/config/makedirs etc. instead of RPM symlinking

%define ic_version			4.7.0
%define ic_rpm_release		1
%define ic_package_basename	interchange
%define ic_user				interch
%define ic_group			interch

# Relevant differences between Red Hat 6 and Red Hat 7 file layout:
# /home/httpd -> /var/www
# /usr/man    -> /usr/share/man  (automatically adjusted in %_mandir)
# /usr/doc    -> /usr/share/doc  (automatically adjusted in %_docdir)

Summary: Interchange - a complete ecommerce system
Name: %ic_package_basename
Version: %ic_version
Release: %ic_rpm_release
Vendor: Red Hat, Inc.
Copyright: GPL
URL: http://ic.redhat.com/
Packager: Jon Jensen <jon@redhat.com>
Source: http://ic.redhat.com/pub/interchange/interchange-%{ic_version}.tar.gz
Group: Applications/Internet
Provides: %ic_package_basename
Obsoletes: %ic_package_basename

BuildRoot: %{_tmppath}/%{name}-%{version}

%description
Interchange is the most powerful free ecommerce system available today.


# Note: This will break the RPM build if more than one catalog is mentioned.
# Maybe someday I can fix this to build multiple demos again ...
%define cat_name foundation

%package %cat_name
Summary: Interchange Foundation catalog - a template for building your own store
Group: Applications/Internet
Requires: %ic_package_basename
Provides: %{ic_package_basename}-%cat_name
Obsoletes: %{ic_package_basename}-%cat_name

%description %cat_name
The Foundation Store is a basic catalog you can adapt to build your own store.


%define warning_file %{_docdir}/%{ic_package_basename}-%{version}/WARNING_YOU_ARE_MISSING_SOMETHING
%define main_filelist %{_tmppath}/%{name}-%{version}.filelist

%prep


%setup


%build

if test -z "$RPM_BUILD_ROOT" -o "$RPM_BUILD_ROOT" = "/"
then
	echo "RPM_BUILD_ROOT has stupid value"
	exit 1
fi
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT

ETCBASE=/etc
RUNBASE=/var/run
LOGBASE=/var/log
LIBBASE=/var/lib
ICBASE=%{_libdir}/interchange

# Create an interch user if one doesn't already exist (on build machine).
if [ -z "`grep '^%{ic_user}:' /etc/passwd`" ]
then
	if [ -n "`grep ^%{ic_group}: /etc/group`" ]
	then
		GROUPOPT='-g %{ic_group}'
	else
		GROUPOPT=
	fi
	useradd -M -r -d $LIBBASE/interchange -s /bin/bash -c "Interchange server" $GROUPOPT %ic_user
fi

perl Makefile.PL \
	rpmbuilddir=$RPM_BUILD_ROOT \
	INTERCHANGE_USER=%ic_user \
	PREFIX=$RPM_BUILD_ROOT%{_libdir}/interchange \
	INSTALLMAN1DIR=$RPM_BUILD_ROOT%{_mandir}/man1 \
	INSTALLMAN3DIR=$RPM_BUILD_ROOT%{_mandir}/man8 \
	force=1
make > /dev/null
make test
make install
gzip $RPM_BUILD_ROOT%{_mandir}/man*/* 2>/dev/null
mkdir -p $RPM_BUILD_ROOT%{_libdir}/interchange/build
cp extra/HTML/Entities.pm $RPM_BUILD_ROOT%{_libdir}/interchange/build
cp extra/IniConf.pm $RPM_BUILD_ROOT%{_libdir}/interchange/build
cp -a eg extensions $RPM_BUILD_ROOT%{_libdir}/interchange
chown -R root.root $RPM_BUILD_ROOT
cd $RPM_BUILD_ROOT%{_libdir}/interchange
export PERL5LIB=$RPM_BUILD_ROOT%{_libdir}/interchange/lib
export MINIVEND_ROOT=$RPM_BUILD_ROOT%{_libdir}/interchange
perl -pi -e "s:^\s+LINK_FILE\s+=>.*:	LINK_FILE => \"$RUNBASE/interchange/socket\",:" bin/compile_link
bin/compile_link -build src

mkdir -p $RPM_BUILD_ROOT$LIBBASE/interchange

ICDIRS="$RPM_BUILD_ROOT$RUNBASE/interchange $RPM_BUILD_ROOT$LOGBASE/interchange"
for i in $ICDIRS
do
	mkdir -p $i
	chown %{ic_user}.%ic_group $i
	chmod 751 $i
done

mkdir -p $RPM_BUILD_ROOT$ETCBASE/rc.d/init.d
cat > $RPM_BUILD_ROOT$ETCBASE/rc.d/init.d/interchange <<EOF
#!/bin/sh
#
# Startup script for Interchange
# http://developer.akopia.com/
#
# chkconfig: 345 96 4
# description: Interchange is a database access and HTML templating system focused on ecommerce
# processname: interchange
# pidfile: $RUNBASE/interchange/interchange.pid
# config: $ETCBASE/interchange.cfg
# config: $LIBBASE/interchange/*/catalog.cfg

# Source function library.
. /etc/rc.d/init.d/functions

# Handle /usr/local
#PATH=\$PATH:/usr/local/bin

# See how we were called.
case "\$1" in
	start)
		echo -n "Starting Interchange: "
		daemon interchange
		echo
		touch /var/lock/subsys/interchange
		;;
	stop)
		echo -n "Shutting down Interchange: "
		killproc interchange
		echo
		rm -f /var/lock/subsys/interchange
		rm -f $RUNBASE/interchange/interchange.pid
		;;
	status)
		status interchange
		;;
	restart)
		\$0 stop
		\$0 start
		;;
	*)
		echo "Usage: \$0 {start|stop|restart|status}"
		exit 1
esac

exit 0
EOF

mkdir -p $RPM_BUILD_ROOT$ETCBASE/logrotate.d
cat > $RPM_BUILD_ROOT$ETCBASE/logrotate.d/interchange <<EOF
/var/log/interchange/*log {
        rotate 4
        weekly
        compress
}
EOF

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
cat > $RPM_BUILD_ROOT%{_sbindir}/interchange <<EOF
#!/bin/sh

RUNSTRING="%{_libdir}/interchange/bin/interchange -q \\
	-configfile $ETCBASE/interchange.cfg \\
	-pidfile $RUNBASE/interchange/interchange.pid \\
	-logfile $LOGBASE/interchange/error.log \\
	ErrorFile=$LOGBASE/interchange/error.log \\
	PIDfile=$RUNBASE/interchange/interchange.pid \\
	-confdir $RUNBASE/interchange \\
	SocketFile=$RUNBASE/interchange/socket"

USER=\`whoami\`
if test \$USER = "root"
then 
	exec su %ic_user -c "\$RUNSTRING \$*"
else
	exec \$RUNSTRING \$*
fi
EOF

chmod +x $RPM_BUILD_ROOT$ETCBASE/rc.d/init.d/interchange \
	$RPM_BUILD_ROOT%{_sbindir}/interchange

find $RPM_BUILD_ROOT%{_libdir}/interchange/bin -type f | xargs chmod 755

mv interchange.cfg.dist $RPM_BUILD_ROOT$ETCBASE/interchange.cfg
ln -s $ETCBASE/interchange.cfg
chmod +r $RPM_BUILD_ROOT$ETCBASE/interchange.cfg

rm -f error.log
ln -s $LOGBASE/interchange/error.log

cd $RPM_BUILD_ROOT
# I don't know of a way to exclude a subdirectory from one of the directories
# listed in the %files section, so I have to use this monstrosity to generate
# a list of all directories in /usr/lib/interchange except the foundation demo
# directory and pass the list to %files below.
DIRDEPTH=`echo $ICBASE | sed 's:[^/]::g' | awk '{print length + 1}'`
find . -path .$ICBASE/%cat_name -prune -mindepth $DIRDEPTH -maxdepth $DIRDEPTH \
	-o -print | grep "^\.$ICBASE" | sed 's:^\.::' > %main_filelist


%install


%pre

if test -x /etc/rc.d/init.d/interchange
then
	/etc/rc.d/init.d/interchange stop > /dev/null 2>&1
	#echo "Giving interchange a couple of seconds to exit nicely"
	sleep 5
fi

# Create an interch user if one doesn't already exist (on install machine).
if [ -z "`grep '^%{ic_user}:' /etc/passwd`" ]
then
	if [ -n "`grep ^%{ic_group}: /etc/group`" ]
	then
		GROUPOPT='-g %{ic_group}'
	else
		GROUPOPT=
	fi
	useradd -M -r -d /var/lib/interchange -s /bin/bash -c "Interchange server" $GROUPOPT %ic_user 2> /dev/null || true 
fi


%files -f %main_filelist

%defattr(-, root, root)

%doc QuickStart
%doc LICENSE
%doc README
%doc README.rpm
%doc README.cvs
%doc WHATSNEW
%doc pdf/icbackoffice.pdf
%doc pdf/icconfig.pdf
%doc pdf/icdatabase.pdf
%doc pdf/icinstall.pdf
%doc pdf/icintro.pdf
%doc pdf/ictemplates.pdf
%doc pdf/icupgrade.pdf
%{_mandir}/man1
%{_mandir}/man8

%{_sbindir}/interchange
/var/log/interchange
/var/run/interchange
%dir /var/lib/interchange

%config(noreplace) /etc/interchange.cfg
%config(noreplace) /etc/rc.d/init.d/interchange
%config(noreplace) /etc/logrotate.d/interchange


%files %cat_name

%defattr(-, root, root)
%{_libdir}/interchange/%cat_name


%post

# Make Interchange start/stop automatically with the operating system.
/sbin/chkconfig --add interchange

# Give interch user ownership of all files the Interchange daemon will
# need read/write access to
chown -R %{ic_user}.%ic_group \
	/var/lib/interchange \
	/var/log/interchange \
	/var/run/interchange

# Get to a place where no random Perl libraries should be found
cd /usr

status=`perl -e "require HTML::Entities and print 1;" 2>/dev/null`
if test "x$status" != x1
then
	mkdir -p %{_libdir}/interchange/lib/HTML 2>/dev/null
	cp %{_libdir}/interchange/build/Entities.pm %{_libdir}/interchange/lib/HTML 2>/dev/null
fi

status=`perl -e "require IniConf and print 1;" 2>/dev/null`
if test "x$status" != x1
then
	cp %{_libdir}/interchange/build/IniConf.pm %{_libdir}/interchange/lib 2>/dev/null
fi

status=`perl -e "require Storable and print 1;" 2>/dev/null`
if test "x$status" != x1
then
	rm -f %{_libdir}/interchange/_*storable
fi

missing=
for i in MD5 MIME::Base64 URI::URL SQL::Statement Safe::Hole
do
	status=`perl -e "require $i and print 1;" 2>/dev/null`
	if test "x$status" != x1
	then
		missing="$missing $i"
	fi
done

if test -n "$missing"
then
	{
		echo ""
		echo "Missing Perl modules:"
		echo ""
		echo "$missing"
		echo ""
		echo "Interchange catalogs will work without them, but the admin interface will not."
		echo "You need to install these modules before you can use the admin interface."
		echo ""
		echo "Try:"
		echo ""
		echo 'perl -MCPAN -e "install Bundle::Interchange"'
		echo ""
	} > %warning_file
fi


%post %cat_name

if [ -d /var/www ]
then
	WEBDIR=/var/www
else
	WEBDIR=/home/httpd
fi

HOST=`hostname`
VENDROOT=%{_libdir}/interchange
BASEDIR=/var/lib/interchange
LOGDIR=/var/log/interchange
DOCROOT=$WEBDIR/html
CGIDIR=$WEBDIR/cgi-bin
CGIBASE=/cgi-bin
SERVERCONF=/etc/httpd/conf/httpd.conf

cd $VENDROOT
pwd
for i in %cat_name
do 
	# build the demo catalog
	mkdir -p $CGIDIR
	mkdir -p $DOCROOT/$i/images
	mkdir $BASEDIR/$i
	bin/makecat \
		-F \
		--demotype=$i \
		--catalogname=$i \
		--basedir=$BASEDIR \
		--catroot=$BASEDIR/$i \
		--documentroot=$DOCROOT \
		--samplehtml=$DOCROOT/$i \
		--sampleurl=http://$HOST/$i \
		--imagedir=$DOCROOT/$i/images \
		--imageurl=/$i/images \
		--sharedir=$DOCROOT \
		--shareurl=/ \
		--cgidir=$CGIDIR \
		--cgibase=$CGIBASE \
		--cgiurl=$CGIBASE/$i \
		--interchangeuser=%ic_user \
		--interchangegroup=%ic_group \
		--permtype=user \
		--serverconf=$SERVERCONF \
		--vendroot=$VENDROOT \
		--linkmode=UNIX \
		--servername=$HOST \
		--catuser=%ic_user \
		--mailorderto=%{ic_user}@$HOST
	touch $LOGDIR/$i.error.log
	ln -sf $LOGDIR/$i.error.log $BASEDIR/$i/error.log
done

# Shouldn't we have makecat take care of these permissions?
find $BASEDIR | xargs chown %{ic_user}.%ic_group
find $BASEDIR -type d | xargs chmod 755

# Restart Interchange to recognize new catalog
%{_sbindir}/interchange -r


%preun

# Stop Interchange if running
if test -x /etc/rc.d/init.d/interchange
then
	/etc/rc.d/init.d/interchange stop > /dev/null
fi

# Remove autostart of interchange
if test $1 = 0
then
	/sbin/chkconfig --del interchange
fi

# Remove non-user data
rm -rf /var/run/interchange/*
rm -rf %{_libdir}/interchange/lib/HTML
rm -f %warning_file
rm -f /var/log/interchange/error.log


%preun %cat_name

# Remove catalog from running Interchange
if test -x %{_sbindir}/interchange
then
	%{_sbindir}/interchange --remove=%{cat_name} > /dev/null
fi

# Remove Catalog directive from interchange.cfg
ICCFG=/etc/interchange.cfg
ICCFGTMP=/tmp/rpm.$$.interchange.cfg
if [ -f $ICCFG ]
then
	grep -v "^[ \t]*Catalog[ \t][ \t]*%{cat_name}[ \t]" $ICCFG > $ICCFGTMP && \
		chown --reference=$ICCFG $ICCFGTMP && \
		chmod --reference=$ICCFG $ICCFGTMP && \
		mv $ICCFGTMP $ICCFG
fi

# Remove foundation store stuff -- we'd rather not do this, but
# Red Hat's certification tests require no files be left over
for i in %cat_name
do
	DEMOCATDIR=/var/lib/interchange/$i
	rm -rf $DEMOCATDIR/tmp/* \
		$DEMOCATDIR/session/* \
		$DEMOCATDIR/logs/* \
		$DEMOCATDIR/images
	rm -f $DEMOCATDIR/products/*.gdbm \
		$DEMOCATDIR/products/Ground.csv.numeric \
		$DEMOCATDIR/products/products.txt.* \
		$DEMOCATDIR/etc/status.$i
done


%clean

rm -f %main_filelist
#[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT


%changelog

* Tue Feb 20 2001 Jon Jensen <jon@redhat.com>
- build separate packages for Interchange server and foundation demo
- run makecat on foundation at install time, rather than build time
  - this shaves around 500 kB from the RPM package size
  - don't need to know web directory at build time now, which brings us
    very close to a single RPM for both RH 6 and 7 platforms; docs are
    now the only difference left
- clean up RPM build root after build
- update text throughout to reflect Red Hat acquisition of Akopia

* Sat Jan  6 2001 Jon Jensen <jon@akopia.com>
- purge global error.log and most of construct demo when uninstalling
  to satisfy Red Hat's RPM certification requirements

* Fri Dec  1 2000 Jon Jensen <jon@akopia.com>
- combined Red Hat 6 and Red Hat 7 specfiles -- target platform is now
  determined by build machine
- fixed bug for HTML::Entities and IniConf installation caused by
  /usr/lib/interchange/build directory not being created
- imported makedirs.redhat and makecat.redhat scripts into specfile
- allow creation of interch user even if interch group already exists
  (relevant only to Red Hat 7 AFAIK)
- numerous other minor modifications
