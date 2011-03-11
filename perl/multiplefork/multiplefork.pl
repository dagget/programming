#!/usr/bin/perl
# Example code of multiple forks with bidirectional communication in perl
#
#
# NOTE: Ik weet dat perl een thread module heeft, maar de perl op onze
# machines ondersteunt dit niet. Deze oplossing is een korte termijn work-
# around, voor een probleem dat we later in c binnen een component gaan
# oplossen.

use warnings;
use strict;
use IO::Socket;
use IO::Select;
use POSIX ":sys_wait_h";

my %filehandles;
my %childprocesses;
my $threadnum;
my $pid;
my $line_received;
my @handles;
my $counter           = 0;
my @animation         = qw( \ | / - );
my $maxnumthreads     = 5;
my $selectlist        = IO::Select->new();


$SIG{CHLD} = \&REAPER;

sub REAPER
{
   my $pid = 0;

   do
   {
      $pid = waitpid(-1, &WNOHANG);
      if ($pid == -1) {
         # no child waiting.  Ignore signal.
      }
      elsif (WIFEXITED($?)) {
         delete $childprocesses{$pid};
      }
   }
   while ($pid > 0);

   $SIG{CHLD} = \&REAPER;  # in case of unreliable signals
}

#### MAIN ####
for ($threadnum = 1; $threadnum <= $maxnumthreads; $threadnum++) {

   # socket pair for bidirectional communication
   socketpair($filehandles{$threadnum}, PARENT, AF_UNIX, SOCK_STREAM, PF_UNSPEC) or die "socketpair: $!";
   $filehandles{$threadnum}->autoflush(1);
   PARENT->autoflush(1);

   $selectlist->add(\*{$filehandles{$threadnum}});

   if ( $pid = fork ) {
      # parent
      close PARENT;

      # keep track of kids
      $childprocesses{$pid} = $pid;
      print {$filehandles{$threadnum}} "Parent (pid $$) is sending this\n";

   } else {
      # child
      my $acktimeout = 0;
      my $line       = "";

      die "cannot fork: $!" unless defined $pid;
      close $filehandles{$threadnum};

      $line = <PARENT>;
      chomp($line);
      print "Child $threadnum (pid $$) just read this: '$line'\n";

      # insert useful task here
      sleep int(rand(10-$threadnum));

      print PARENT "Child $threadnum (pid $$) is sending this\n";

      # Sync parent & child
      # Tell parent child is done writing (parent will get EOF when reading)
      shutdown(PARENT,1);

      # Wait for parent to acknowledge all data has been read
      while ( !eof(PARENT) ){
         sleep(1);
         $acktimeout++;
         $acktimeout >= 60 and exit(1);
      }

      exit(0);
   }
}

while (keys %childprocesses > 0) {

   if (@handles = $selectlist->can_read(0)){

      foreach my $handle ( @handles ) {
         recv($handle, $line_received, 1024, 0);
         chomp($line_received);
         length $line_received > 0 and print "Parent Pid $$ just read this: '$line_received'\n";

         # Sync parent & child
         # Acknowledge parent has read all child had to say (child will get EOF when reading)
         length $line_received == 0 and shutdown($handle,1);
      }
   }

   # animation to show progress
   local $| = 1;
   print "$animation[$counter++]\b";
   $counter = 0 if $counter == scalar(@animation);

   sleep(1);
}

print "DONE\n";
exit(0);
