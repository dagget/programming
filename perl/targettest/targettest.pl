#!/usr/bin/perl
#
use warnings;
use strict;
use Getopt::Long;
use Net::Ping;
use Net::FTP;
use Net::Rsh;

my %targetlist=(
	"Target1" => 0,
	"Target2" => 0,
	"Target3" => 0,
	"localhost" => 0
	);

my %Options;

# collect list of files to put on target
# collect list of files to save from target
GetOptions(\%Options, "filestotarget=s@", "resultfiles=s@", "filesfromtarget=s@") or die "Failed to retrieve correct options";

# collect list of files to remove from target
!defined $Options{"filesfromtarget"} and $Options{"filesfromtarget"} = $Options{"filestotarget"};

# ping list of possible targets
my $p = Net::Ping->new("icmp");
my $the_target;
my $ftpusr = "root";
my $ftppwd = "root";
my $ftploc = "/bct";

while( my ($k, $v) = each %targetlist ) 
{
	print "Pinging target: $k.\n";
	if ($p->ping($k,2)) {
		$targetlist{$k} = 1;
		$the_target = $k;
		print "Using target $the_target.\n";
		last;
	} 
	sleep(1);
}
$p->close();

# ftp stuff to first available target
my $ftp = Net::FTP->new($the_target, Debug => 0) or die "Cannot connect to $the_target: $@";
$ftp->login($ftpusr,$ftppwd) or die "Cannot login ", $ftp->message;
$ftp->cwd($ftploc) or die "Cannot change working directory ", $ftp->message;
foreach ($Options{"filestotarget"})
{
	print "Putting $_ on the target\n";
	$ftp->put($_) or die "put failed ", $ftp->message;
}
$ftp->quit;

# ssh to perform test
$a=Net::Rsh->new();

$host="cisco.router.com";
$local_user=`id`;
chomp($local_user);
$remote_user=$ftpusr;
$cmd="sh ru";

@c=$a->rsh($the_target,$local_user,$remote_user,$cmd);
print @c;

# ftp stuff from target
$ftp = Net::FTP->new($the_target, Debug => 0) or die "Cannot connect to $the_target: $@";
$ftp->login($ftpusr,$ftppwd) or die "Cannot login ", $ftp->message;
$ftp->cwd($ftploc) or die "Cannot change working directory ", $ftp->message;
foreach ($Options{"resultfiles"})
{
	print "Getting $_ off the target\n";
	$ftp->get($_) or die "get failed ", $ftp->message;
}
$ftp->quit;

# ftp to remove stuff off target
$ftp = Net::FTP->new($the_target, Debug => 0) or die "Cannot connect to $the_target: $@";
$ftp->login($ftpusr,$ftppwd) or die "Cannot login ", $ftp->message;
$ftp->cwd($ftploc) or die "Cannot change working directory ", $ftp->message;
foreach ($Options{"filesfromtarget"})
{
	print "Removing $_ off the target\n";
	$ftp->delete($_) or warn "delete failed ", $ftp->message;
}
$ftp->quit;

exit(0);
