package Bio::KBase::Catalog::Client;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

Bio::KBase::Catalog::Client

=head1 DESCRIPTION


Service for managing, registering, and building KBase Modules.


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => Bio::KBase::Catalog::Client::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my $token = Bio::KBase::AuthToken->new(@args);
	
	if (!$token->error_message)
	{
	    $self->{token} = $token->token;
	    $self->{client}->{token} = $token->token;
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 version

  $version = $obj->version()

=over 4

=item Parameter and return types

=begin html

<pre>
$version is a string

</pre>

=end html

=begin text

$version is a string


=end text

=item Description

Get the version of the deployed catalog service endpoint.

=back

=cut

 sub version
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 0)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function version (received $n, expecting 0)");
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.version",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'version',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method version",
					    status_line => $self->{client}->status_line,
					    method_name => 'version',
				       );
    }
}
 


=head2 is_registered

  $return = $obj->is_registered($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectOneModuleParams
$return is a Catalog.boolean
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.SelectOneModuleParams
$return is a Catalog.boolean
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
boolean is an int


=end text

=item Description



=back

=cut

 sub is_registered
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function is_registered (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to is_registered:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'is_registered');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.is_registered",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'is_registered',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method is_registered",
					    status_line => $self->{client}->status_line,
					    method_name => 'is_registered',
				       );
    }
}
 


=head2 register_repo

  $timestamp = $obj->register_repo($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.RegisterRepoParams
$timestamp is an int
RegisterRepoParams is a reference to a hash where the following keys are defined:
	git_url has a value which is a string
	git_commit_hash has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.RegisterRepoParams
$timestamp is an int
RegisterRepoParams is a reference to a hash where the following keys are defined:
	git_url has a value which is a string
	git_commit_hash has a value which is a string


=end text

=item Description

allow/require developer to supply git branch/git commit tag? 
if this is a new module, creates the initial registration with the authenticated user as
the sole owner, then launches a build to update the dev version of the module.  You can check
the state of this build with the 'get_module_state' method passing in the git_url.  If the module
already exists, then you must be an owner to reregister.  That will immediately overwrite your
dev version of the module (old dev versions are not stored, but you can always reregister an old
version from the repo) and start a build.

=back

=cut

 sub register_repo
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function register_repo (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to register_repo:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'register_repo');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.register_repo",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'register_repo',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method register_repo",
					    status_line => $self->{client}->status_line,
					    method_name => 'register_repo',
				       );
    }
}
 


=head2 push_dev_to_beta

  $obj->push_dev_to_beta($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectOneModuleParams
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.SelectOneModuleParams
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string


=end text

=item Description

immediately updates the beta tag to what is currently in dev, whatever is currently in beta
is discarded.  Will fail if a release request is active and has not been approved/denied

=back

=cut

 sub push_dev_to_beta
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function push_dev_to_beta (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to push_dev_to_beta:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'push_dev_to_beta');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.push_dev_to_beta",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'push_dev_to_beta',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method push_dev_to_beta",
					    status_line => $self->{client}->status_line,
					    method_name => 'push_dev_to_beta',
				       );
    }
}
 


=head2 request_release

  $obj->request_release($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectOneModuleParams
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.SelectOneModuleParams
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string


=end text

=item Description

requests a push from beta to release version; must be approved be a kbase Admin

=back

=cut

 sub request_release
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function request_release (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to request_release:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'request_release');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.request_release",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'request_release',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method request_release",
					    status_line => $self->{client}->status_line,
					    method_name => 'request_release',
				       );
    }
}
 


=head2 list_requested_releases

  $requested_releases = $obj->list_requested_releases()

=over 4

=item Parameter and return types

=begin html

<pre>
$requested_releases is a reference to a list where each element is a Catalog.RequestedReleaseInfo
RequestedReleaseInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	timestamp has a value which is a string
	owners has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$requested_releases is a reference to a list where each element is a Catalog.RequestedReleaseInfo
RequestedReleaseInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	timestamp has a value which is a string
	owners has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub list_requested_releases
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 0)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_requested_releases (received $n, expecting 0)");
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_requested_releases",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_requested_releases',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_requested_releases",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_requested_releases',
				       );
    }
}
 


=head2 review_release_request

  $obj->review_release_request($review)

=over 4

=item Parameter and return types

=begin html

<pre>
$review is a Catalog.ReleaseReview
ReleaseReview is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	decision has a value which is a string
	review_message has a value which is a string

</pre>

=end html

=begin text

$review is a Catalog.ReleaseReview
ReleaseReview is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	decision has a value which is a string
	review_message has a value which is a string


=end text

=item Description



=back

=cut

 sub review_release_request
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function review_release_request (received $n, expecting 1)");
    }
    {
	my($review) = @args;

	my @_bad_arguments;
        (ref($review) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"review\" (value was \"$review\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to review_release_request:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'review_release_request');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.review_release_request",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'review_release_request',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method review_release_request",
					    status_line => $self->{client}->status_line,
					    method_name => 'review_release_request',
				       );
    }
}
 


=head2 list_basic_module_info

  $info_list = $obj->list_basic_module_info($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ListModuleParams
$info_list is a reference to a list where each element is a Catalog.BasicModuleInfo
ListModuleParams is a reference to a hash where the following keys are defined:
	include_unreleased has a value which is a Catalog.boolean
	include_disabled has a value which is a Catalog.boolean
boolean is an int
BasicModuleInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.ListModuleParams
$info_list is a reference to a list where each element is a Catalog.BasicModuleInfo
ListModuleParams is a reference to a hash where the following keys are defined:
	include_unreleased has a value which is a Catalog.boolean
	include_disabled has a value which is a Catalog.boolean
boolean is an int
BasicModuleInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string


=end text

=item Description



=back

=cut

 sub list_basic_module_info
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_basic_module_info (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_basic_module_info:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_basic_module_info');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_basic_module_info",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_basic_module_info',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_basic_module_info",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_basic_module_info',
				       );
    }
}
 


=head2 get_module_info

  $info = $obj->get_module_info($selection)

=over 4

=item Parameter and return types

=begin html

<pre>
$selection is a Catalog.SelectOneModuleParams
$info is a Catalog.ModuleInfo
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	description has a value which is a string
	language has a value which is a string
	owners has a value which is a reference to a list where each element is a string
	release has a value which is a Catalog.ModuleVersionInfo
	beta has a value which is a Catalog.ModuleVersionInfo
	dev has a value which is a Catalog.ModuleVersionInfo
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$selection is a Catalog.SelectOneModuleParams
$info is a Catalog.ModuleInfo
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	description has a value which is a string
	language has a value which is a string
	owners has a value which is a reference to a list where each element is a string
	release has a value which is a Catalog.ModuleVersionInfo
	beta has a value which is a Catalog.ModuleVersionInfo
	dev has a value which is a Catalog.ModuleVersionInfo
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_module_info
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_module_info (received $n, expecting 1)");
    }
    {
	my($selection) = @args;

	my @_bad_arguments;
        (ref($selection) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"selection\" (value was \"$selection\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_module_info:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_module_info');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_module_info",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_module_info',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_module_info",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_module_info',
				       );
    }
}
 


=head2 get_version_info

  $version = $obj->get_version_info($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectModuleVersionParams
$version is a Catalog.ModuleVersionInfo
SelectModuleVersionParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	version has a value which is a string
	owner_version_string has a value which is a string
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.SelectModuleVersionParams
$version is a Catalog.ModuleVersionInfo
SelectModuleVersionParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	version has a value which is a string
	owner_version_string has a value which is a string
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_version_info
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_version_info (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_version_info:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_version_info');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_version_info",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_version_info',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_version_info",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_version_info',
				       );
    }
}
 


=head2 list_released_module_versions

  $versions = $obj->list_released_module_versions($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectOneModuleParams
$versions is a reference to a list where each element is a Catalog.ModuleVersionInfo
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.SelectOneModuleParams
$versions is a reference to a list where each element is a Catalog.ModuleVersionInfo
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub list_released_module_versions
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_released_module_versions (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_released_module_versions:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_released_module_versions');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_released_module_versions",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_released_module_versions',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_released_module_versions",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_released_module_versions',
				       );
    }
}
 


=head2 set_registration_state

  $obj->set_registration_state($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SetRegistrationStateParams
SetRegistrationStateParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	registration_state has a value which is a string
	error_message has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.SetRegistrationStateParams
SetRegistrationStateParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	registration_state has a value which is a string
	error_message has a value which is a string


=end text

=item Description



=back

=cut

 sub set_registration_state
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function set_registration_state (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to set_registration_state:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'set_registration_state');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.set_registration_state",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'set_registration_state',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method set_registration_state",
					    status_line => $self->{client}->status_line,
					    method_name => 'set_registration_state',
				       );
    }
}
 


=head2 get_module_state

  $state = $obj->get_module_state($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectOneModuleParams
$state is a Catalog.ModuleState
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleState is a reference to a hash where the following keys are defined:
	active has a value which is a Catalog.boolean
	release_approval has a value which is a string
	review_message has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.SelectOneModuleParams
$state is a Catalog.ModuleState
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
ModuleState is a reference to a hash where the following keys are defined:
	active has a value which is a Catalog.boolean
	release_approval has a value which is a string
	review_message has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string
boolean is an int


=end text

=item Description

Get repo state (one of 'pending', 'ready', 'building', 'testing', 'disabled').

=back

=cut

 sub get_module_state
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_module_state (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_module_state:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_module_state');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_module_state",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_module_state',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_module_state",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_module_state',
				       );
    }
}
 


=head2 get_build_log

  $return = $obj->get_build_log($timestamp)

=over 4

=item Parameter and return types

=begin html

<pre>
$timestamp is a string
$return is a string

</pre>

=end html

=begin text

$timestamp is a string
$return is a string


=end text

=item Description



=back

=cut

 sub get_build_log
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_build_log (received $n, expecting 1)");
    }
    {
	my($timestamp) = @args;

	my @_bad_arguments;
        (!ref($timestamp)) or push(@_bad_arguments, "Invalid type for argument 1 \"timestamp\" (value was \"$timestamp\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_build_log:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_build_log');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_build_log",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_build_log',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_build_log",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_build_log',
				       );
    }
}
 
  

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "Catalog.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'get_build_log',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method get_build_log",
            status_line => $self->{client}->status_line,
            method_name => 'get_build_log',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for Bio::KBase::Catalog::Client\n";
    }
    if ($sMajor == 0) {
        warn "Bio::KBase::Catalog::Client version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

@range [0,1]


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 SelectOneModuleParams

=over 4



=item Description

Describes how to find module/repository.
module_name - name of module defined in kbase.yaml file;
git_url - the url used to register the module


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string


=end text

=back



=head2 RegisterRepoParams

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
git_url has a value which is a string
git_commit_hash has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
git_url has a value which is a string
git_commit_hash has a value which is a string


=end text

=back



=head2 RequestedReleaseInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
timestamp has a value which is a string
owners has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
timestamp has a value which is a string
owners has a value which is a reference to a list where each element is a string


=end text

=back



=head2 ReleaseReview

=over 4



=item Description

decision - approved | denied
review_message -


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
decision has a value which is a string
review_message has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
decision has a value which is a string
review_message has a value which is a string


=end text

=back



=head2 ListModuleParams

=over 4



=item Description

Describes how to filter repositories.
include_unreleased - optional flag indicated modules that are not released are included (default:false)
with_disabled - optional flag indicating disabled repos should be included (default:false).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean


=end text

=back



=head2 BasicModuleInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string


=end text

=back



=head2 ModuleVersionInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
timestamp has a value which is an int
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
narrative_method_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
timestamp has a value which is an int
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
narrative_method_ids has a value which is a reference to a list where each element is a string


=end text

=back



=head2 ModuleInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
description has a value which is a string
language has a value which is a string
owners has a value which is a reference to a list where each element is a string
release has a value which is a Catalog.ModuleVersionInfo
beta has a value which is a Catalog.ModuleVersionInfo
dev has a value which is a Catalog.ModuleVersionInfo

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
description has a value which is a string
language has a value which is a string
owners has a value which is a reference to a list where each element is a string
release has a value which is a Catalog.ModuleVersionInfo
beta has a value which is a Catalog.ModuleVersionInfo
dev has a value which is a Catalog.ModuleVersionInfo


=end text

=back



=head2 SelectModuleVersionParams

=over 4



=item Description

only required: module_name or git_url, the rest are optional selectors
If no selectors given, returns current release version
version - release | beta | dev
owner_version_string - matches on the 'version' set for a version in 'kbase.yaml'


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
version has a value which is a string
owner_version_string has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
version has a value which is a string
owner_version_string has a value which is a string


=end text

=back



=head2 SetRegistrationStateParams

=over 4



=item Description

Describes how to find repository details.
module_name - name of module defined in kbase.yaml file;
multiple state fields? (approvalState, buildState, versionState)
state - one of 'pending', 'ready', 'building', 'testing', 'disabled'.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
registration_state has a value which is a string
error_message has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
registration_state has a value which is a string
error_message has a value which is a string


=end text

=back



=head2 ModuleState

=over 4



=item Description

active: True | False,
release_approval: approved | denied | under_review | not_requested, (all releases require approval)
review_message: str, (optional)
registration: building | complete | error,
error_message: str (optional)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
active has a value which is a Catalog.boolean
release_approval has a value which is a string
review_message has a value which is a string
registration has a value which is a string
error_message has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
active has a value which is a Catalog.boolean
release_approval has a value which is a string
review_message has a value which is a string
registration has a value which is a string
error_message has a value which is a string


=end text

=back



=cut

package Bio::KBase::Catalog::Client::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
