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


Service for managing, registering, and building KBase Modules using the KBase SDK.


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

returns true (1) if the module exists, false (2) otherwise

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

  $registration_id = $obj->register_repo($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.RegisterRepoParams
$registration_id is a string
RegisterRepoParams is a reference to a hash where the following keys are defined:
	git_url has a value which is a string
	git_commit_hash has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.RegisterRepoParams
$registration_id is a string
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
	timestamp has a value which is an int
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
	timestamp has a value which is an int
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
	owners has a value which is a reference to a list where each element is a string
	include_released has a value which is a Catalog.boolean
	include_unreleased has a value which is a Catalog.boolean
	include_disabled has a value which is a Catalog.boolean
	include_apps has a value which is a Catalog.boolean
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
	owners has a value which is a reference to a list where each element is a string
	include_released has a value which is a Catalog.boolean
	include_unreleased has a value which is a Catalog.boolean
	include_disabled has a value which is a Catalog.boolean
	include_apps has a value which is a Catalog.boolean
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
 


=head2 add_favorite

  $obj->add_favorite($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string


=end text

=item Description



=back

=cut

 sub add_favorite
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function add_favorite (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to add_favorite:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'add_favorite');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.add_favorite",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'add_favorite',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method add_favorite",
					    status_line => $self->{client}->status_line,
					    method_name => 'add_favorite',
				       );
    }
}
 


=head2 remove_favorite

  $obj->remove_favorite($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string


=end text

=item Description



=back

=cut

 sub remove_favorite
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function remove_favorite (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to remove_favorite:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'remove_favorite');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.remove_favorite",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'remove_favorite',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method remove_favorite",
					    status_line => $self->{client}->status_line,
					    method_name => 'remove_favorite',
				       );
    }
}
 


=head2 list_favorites

  $favorites = $obj->list_favorites($username)

=over 4

=item Parameter and return types

=begin html

<pre>
$username is a string
$favorites is a reference to a list where each element is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string

</pre>

=end html

=begin text

$username is a string
$favorites is a reference to a list where each element is a Catalog.FavoriteItem
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string


=end text

=item Description



=back

=cut

 sub list_favorites
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_favorites (received $n, expecting 1)");
    }
    {
	my($username) = @args;

	my @_bad_arguments;
        (!ref($username)) or push(@_bad_arguments, "Invalid type for argument 1 \"username\" (value was \"$username\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_favorites:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_favorites');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_favorites",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_favorites',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_favorites",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_favorites',
				       );
    }
}
 


=head2 list_app_favorites

  $users = $obj->list_app_favorites($item)

=over 4

=item Parameter and return types

=begin html

<pre>
$item is a Catalog.FavoriteItem
$users is a reference to a list where each element is a Catalog.FavoriteUser
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string
FavoriteUser is a reference to a hash where the following keys are defined:
	username has a value which is a string
	timestamp has a value which is a string

</pre>

=end html

=begin text

$item is a Catalog.FavoriteItem
$users is a reference to a list where each element is a Catalog.FavoriteUser
FavoriteItem is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	id has a value which is a string
FavoriteUser is a reference to a hash where the following keys are defined:
	username has a value which is a string
	timestamp has a value which is a string


=end text

=item Description



=back

=cut

 sub list_app_favorites
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_app_favorites (received $n, expecting 1)");
    }
    {
	my($item) = @args;

	my @_bad_arguments;
        (ref($item) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"item\" (value was \"$item\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_app_favorites:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_app_favorites');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_app_favorites",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_app_favorites',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_app_favorites",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_app_favorites',
				       );
    }
}
 


=head2 list_favorite_counts

  $counts = $obj->list_favorite_counts($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ListFavoriteCounts
$counts is a reference to a list where each element is a Catalog.FavoriteCount
ListFavoriteCounts is a reference to a hash where the following keys are defined
FavoriteCount is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	app_id has a value which is a string
	count has a value which is an int

</pre>

=end html

=begin text

$params is a Catalog.ListFavoriteCounts
$counts is a reference to a list where each element is a Catalog.FavoriteCount
ListFavoriteCounts is a reference to a hash where the following keys are defined
FavoriteCount is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	app_id has a value which is a string
	count has a value which is an int


=end text

=item Description



=back

=cut

 sub list_favorite_counts
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_favorite_counts (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_favorite_counts:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_favorite_counts');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_favorite_counts",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_favorite_counts',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_favorite_counts",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_favorite_counts',
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
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string

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
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string


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
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string

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
ModuleVersionInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string


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
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string

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
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	narrative_method_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string


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
	released has a value which is a Catalog.boolean
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
	released has a value which is a Catalog.boolean
	release_approval has a value which is a string
	review_message has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string
boolean is an int


=end text

=item Description



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

  $return = $obj->get_build_log($registration_id)

=over 4

=item Parameter and return types

=begin html

<pre>
$registration_id is a string
$return is a string

</pre>

=end html

=begin text

$registration_id is a string
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
	my($registration_id) = @args;

	my @_bad_arguments;
        (!ref($registration_id)) or push(@_bad_arguments, "Invalid type for argument 1 \"registration_id\" (value was \"$registration_id\")");
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
 


=head2 get_parsed_build_log

  $build_log = $obj->get_parsed_build_log($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.GetBuildLogParams
$build_log is a Catalog.BuildLog
GetBuildLogParams is a reference to a hash where the following keys are defined:
	registration_id has a value which is a string
	skip has a value which is an int
	limit has a value which is an int
	first_n has a value which is an int
	last_n has a value which is an int
BuildLog is a reference to a hash where the following keys are defined:
	registration_id has a value which is a string
	timestamp has a value which is a string
	module_name_lc has a value which is a string
	git_url has a value which is a string
	error has a value which is a string
	registration has a value which is a string
	log has a value which is a reference to a list where each element is a Catalog.BuildLogLine
BuildLogLine is a reference to a hash where the following keys are defined:
	content has a value which is a string
	error has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.GetBuildLogParams
$build_log is a Catalog.BuildLog
GetBuildLogParams is a reference to a hash where the following keys are defined:
	registration_id has a value which is a string
	skip has a value which is an int
	limit has a value which is an int
	first_n has a value which is an int
	last_n has a value which is an int
BuildLog is a reference to a hash where the following keys are defined:
	registration_id has a value which is a string
	timestamp has a value which is a string
	module_name_lc has a value which is a string
	git_url has a value which is a string
	error has a value which is a string
	registration has a value which is a string
	log has a value which is a reference to a list where each element is a Catalog.BuildLogLine
BuildLogLine is a reference to a hash where the following keys are defined:
	content has a value which is a string
	error has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description

given the registration_id returned from the register method, you can check the build log with this method

=back

=cut

 sub get_parsed_build_log
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_parsed_build_log (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_parsed_build_log:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_parsed_build_log');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_parsed_build_log",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_parsed_build_log',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_parsed_build_log",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_parsed_build_log',
				       );
    }
}
 


=head2 list_builds

  $builds = $obj->list_builds($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ListBuildParams
$builds is a reference to a list where each element is a Catalog.BuildInfo
ListBuildParams is a reference to a hash where the following keys are defined:
	only_runnning has a value which is a Catalog.boolean
	only_error has a value which is a Catalog.boolean
	only_complete has a value which is a Catalog.boolean
	skip has a value which is an int
	limit has a value which is an int
	modules has a value which is a reference to a list where each element is a Catalog.SelectOneModuleParams
boolean is an int
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
BuildInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is a string
	registration_id has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string
	module_name_lc has a value which is a string
	git_url has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.ListBuildParams
$builds is a reference to a list where each element is a Catalog.BuildInfo
ListBuildParams is a reference to a hash where the following keys are defined:
	only_runnning has a value which is a Catalog.boolean
	only_error has a value which is a Catalog.boolean
	only_complete has a value which is a Catalog.boolean
	skip has a value which is an int
	limit has a value which is an int
	modules has a value which is a reference to a list where each element is a Catalog.SelectOneModuleParams
boolean is an int
SelectOneModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
BuildInfo is a reference to a hash where the following keys are defined:
	timestamp has a value which is a string
	registration_id has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string
	module_name_lc has a value which is a string
	git_url has a value which is a string


=end text

=item Description



=back

=cut

 sub list_builds
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_builds (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_builds:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_builds');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_builds",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_builds',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_builds",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_builds',
				       );
    }
}
 


=head2 delete_module

  $obj->delete_module($params)

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

admin method to delete a module, will only work if the module has not been released

=back

=cut

 sub delete_module
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function delete_module (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to delete_module:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'delete_module');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.delete_module",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'delete_module',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method delete_module",
					    status_line => $self->{client}->status_line,
					    method_name => 'delete_module',
				       );
    }
}
 


=head2 migrate_module_to_new_git_url

  $obj->migrate_module_to_new_git_url($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.UpdateGitUrlParams
UpdateGitUrlParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	current_git_url has a value which is a string
	new_git_url has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.UpdateGitUrlParams
UpdateGitUrlParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	current_git_url has a value which is a string
	new_git_url has a value which is a string


=end text

=item Description

admin method to move the git url for a module, should only be used if the exact same code has migrated to
a new URL.  It should not be used as a way to change ownership, get updates from a new source, or get a new
module name for an existing git url because old versions are retained and git commits saved will no longer
be correct.

=back

=cut

 sub migrate_module_to_new_git_url
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function migrate_module_to_new_git_url (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to migrate_module_to_new_git_url:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'migrate_module_to_new_git_url');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.migrate_module_to_new_git_url",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'migrate_module_to_new_git_url',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method migrate_module_to_new_git_url",
					    status_line => $self->{client}->status_line,
					    method_name => 'migrate_module_to_new_git_url',
				       );
    }
}
 


=head2 set_to_active

  $obj->set_to_active($params)

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

admin methods to turn on/off modules

=back

=cut

 sub set_to_active
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function set_to_active (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to set_to_active:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'set_to_active');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.set_to_active",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'set_to_active',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method set_to_active",
					    status_line => $self->{client}->status_line,
					    method_name => 'set_to_active',
				       );
    }
}
 


=head2 set_to_inactive

  $obj->set_to_inactive($params)

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



=back

=cut

 sub set_to_inactive
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function set_to_inactive (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to set_to_inactive:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'set_to_inactive');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.set_to_inactive",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'set_to_inactive',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method set_to_inactive",
					    status_line => $self->{client}->status_line,
					    method_name => 'set_to_inactive',
				       );
    }
}
 


=head2 is_approved_developer

  $is_approved = $obj->is_approved_developer($usernames)

=over 4

=item Parameter and return types

=begin html

<pre>
$usernames is a reference to a list where each element is a string
$is_approved is a reference to a list where each element is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$usernames is a reference to a list where each element is a string
$is_approved is a reference to a list where each element is a Catalog.boolean
boolean is an int


=end text

=item Description

temporary developer approval, should be moved to more mature user profile service

=back

=cut

 sub is_approved_developer
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function is_approved_developer (received $n, expecting 1)");
    }
    {
	my($usernames) = @args;

	my @_bad_arguments;
        (ref($usernames) eq 'ARRAY') or push(@_bad_arguments, "Invalid type for argument 1 \"usernames\" (value was \"$usernames\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to is_approved_developer:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'is_approved_developer');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.is_approved_developer",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'is_approved_developer',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method is_approved_developer",
					    status_line => $self->{client}->status_line,
					    method_name => 'is_approved_developer',
				       );
    }
}
 


=head2 list_approved_developers

  $usernames = $obj->list_approved_developers()

=over 4

=item Parameter and return types

=begin html

<pre>
$usernames is a reference to a list where each element is a string

</pre>

=end html

=begin text

$usernames is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub list_approved_developers
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 0)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_approved_developers (received $n, expecting 0)");
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_approved_developers",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_approved_developers',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_approved_developers",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_approved_developers',
				       );
    }
}
 


=head2 approve_developer

  $obj->approve_developer($username)

=over 4

=item Parameter and return types

=begin html

<pre>
$username is a string

</pre>

=end html

=begin text

$username is a string


=end text

=item Description



=back

=cut

 sub approve_developer
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function approve_developer (received $n, expecting 1)");
    }
    {
	my($username) = @args;

	my @_bad_arguments;
        (!ref($username)) or push(@_bad_arguments, "Invalid type for argument 1 \"username\" (value was \"$username\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to approve_developer:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'approve_developer');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.approve_developer",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'approve_developer',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method approve_developer",
					    status_line => $self->{client}->status_line,
					    method_name => 'approve_developer',
				       );
    }
}
 


=head2 revoke_developer

  $obj->revoke_developer($username)

=over 4

=item Parameter and return types

=begin html

<pre>
$username is a string

</pre>

=end html

=begin text

$username is a string


=end text

=item Description



=back

=cut

 sub revoke_developer
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function revoke_developer (received $n, expecting 1)");
    }
    {
	my($username) = @args;

	my @_bad_arguments;
        (!ref($username)) or push(@_bad_arguments, "Invalid type for argument 1 \"username\" (value was \"$username\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to revoke_developer:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'revoke_developer');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.revoke_developer",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'revoke_developer',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method revoke_developer",
					    status_line => $self->{client}->status_line,
					    method_name => 'revoke_developer',
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
                method_name => 'revoke_developer',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method revoke_developer",
            status_line => $self->{client}->status_line,
            method_name => 'revoke_developer',
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

Describes how to find a single module/repository.
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
timestamp has a value which is an int
owners has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
timestamp has a value which is an int
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



=head2 AppInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
id has a value which is a string
stars has a value which is an int
runs has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
id has a value which is a string
stars has a value which is an int
runs has a value which is an int


=end text

=back



=head2 Icon

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined
</pre>

=end html

=begin text

a reference to a hash where the following keys are defined

=end text

=back



=head2 ListModuleParams

=over 4



=item Description

Describes how to filter repositories.
include_released - optional flag indicated modules that are released are included (default:true)
include_unreleased - optional flag indicated modules that are not released are included (default:false)
with_disabled - optional flag indicating disabled repos should be included (default:false).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
owners has a value which is a reference to a list where each element is a string
include_released has a value which is a Catalog.boolean
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean
include_apps has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
owners has a value which is a reference to a list where each element is a string
include_released has a value which is a Catalog.boolean
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean
include_apps has a value which is a Catalog.boolean


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



=head2 FavoriteItem

=over 4



=item Description

FAVORITES!!


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
id has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
id has a value which is a string


=end text

=back



=head2 FavoriteUser

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
username has a value which is a string
timestamp has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
username has a value which is a string
timestamp has a value which is a string


=end text

=back



=head2 ListFavoriteCounts

=over 4



=item Description

if favorite item is given, will return stars just for that item.  If a module
name is given, will return stars for all methods in that module.  If none of
those are given, then will return stars for every method that there is info on 

parameters to add:
    list<FavoriteItem> items;
    list<string> module_names;


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined
</pre>

=end html

=begin text

a reference to a hash where the following keys are defined

=end text

=back



=head2 FavoriteCount

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
app_id has a value which is a string
count has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
app_id has a value which is a string
count has a value which is an int


=end text

=back



=head2 ModuleVersionInfo

=over 4



=item Description

data_folder - optional field representing unique module name (like <module_name> transformed to
    lower cases) used for reference data purposes (see description for data_version field). This
    value will be treated as part of file system path relative to the base that comes from the 
    config (currently base is supposed to be "/kb/data" defined in "ref-data-base" parameter).
data_version - optional field, reflects version of data defined in kbase.yml (see "data-version" 
    key). In case this field is set data folder with path "/kb/data/<data_folder>/<data_version>"
    should be initialized by running docker image with "init" target from catalog. And later when
    async methods are run it should be mounted on AWE worker machine into "/data" folder inside 
    docker container by execution engine.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
timestamp has a value which is an int
registration_id has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
narrative_method_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
timestamp has a value which is an int
registration_id has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
narrative_method_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string


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
version is one of: release | beta | dev
old release versions can only be retrieved individually by timestamp or git_commit_hash

Note: this method isn't particularly smart or effecient yet, because it pulls the info for a particular
module first, then searches in code for matches to the relevant query.  Instead, this should be
performed on the database side through queries.  Will optimize when this becomes an issue.

In the future, this will be extended so that you can retrieve version info by only
timestamp, git commit, etc, but the necessary indicies have not been setup yet.  In general, we will
need to add better search capabilities


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
version has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
version has a value which is a string


=end text

=back



=head2 SetRegistrationStateParams

=over 4



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
registration: complete | error | (build state status),
error_message: str (optional)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
active has a value which is a Catalog.boolean
released has a value which is a Catalog.boolean
release_approval has a value which is a string
review_message has a value which is a string
registration has a value which is a string
error_message has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
active has a value which is a Catalog.boolean
released has a value which is a Catalog.boolean
release_approval has a value which is a string
review_message has a value which is a string
registration has a value which is a string
error_message has a value which is a string


=end text

=back



=head2 GetBuildLogParams

=over 4



=item Description

must specify skip & limit, or first_n, or last_n.  If none given, this gets last 5000 lines


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
registration_id has a value which is a string
skip has a value which is an int
limit has a value which is an int
first_n has a value which is an int
last_n has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
registration_id has a value which is a string
skip has a value which is an int
limit has a value which is an int
first_n has a value which is an int
last_n has a value which is an int


=end text

=back



=head2 BuildLogLine

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
content has a value which is a string
error has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
content has a value which is a string
error has a value which is a Catalog.boolean


=end text

=back



=head2 BuildLog

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
registration_id has a value which is a string
timestamp has a value which is a string
module_name_lc has a value which is a string
git_url has a value which is a string
error has a value which is a string
registration has a value which is a string
log has a value which is a reference to a list where each element is a Catalog.BuildLogLine

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
registration_id has a value which is a string
timestamp has a value which is a string
module_name_lc has a value which is a string
git_url has a value which is a string
error has a value which is a string
registration has a value which is a string
log has a value which is a reference to a list where each element is a Catalog.BuildLogLine


=end text

=back



=head2 BuildInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
timestamp has a value which is a string
registration_id has a value which is a string
registration has a value which is a string
error_message has a value which is a string
module_name_lc has a value which is a string
git_url has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
timestamp has a value which is a string
registration_id has a value which is a string
registration has a value which is a string
error_message has a value which is a string
module_name_lc has a value which is a string
git_url has a value which is a string


=end text

=back



=head2 ListBuildParams

=over 4



=item Description

Always sorted by time, oldest builds are last.

only one of these can be set to true:
    only_running - if true, only show running builds
    only_error - if true, only show builds that ended in an error
    only_complete - if true, only show builds that are complete
skip - skip these first n records, default 0
limit - limit result to the most recent n records, default 1000

modules - only include builds from these modules based on names/git_urls


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
only_runnning has a value which is a Catalog.boolean
only_error has a value which is a Catalog.boolean
only_complete has a value which is a Catalog.boolean
skip has a value which is an int
limit has a value which is an int
modules has a value which is a reference to a list where each element is a Catalog.SelectOneModuleParams

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
only_runnning has a value which is a Catalog.boolean
only_error has a value which is a Catalog.boolean
only_complete has a value which is a Catalog.boolean
skip has a value which is an int
limit has a value which is an int
modules has a value which is a reference to a list where each element is a Catalog.SelectOneModuleParams


=end text

=back



=head2 UpdateGitUrlParams

=over 4



=item Description

all fields are required to make sure you update the right one


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
current_git_url has a value which is a string
new_git_url has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
current_git_url has a value which is a string
new_git_url has a value which is a string


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
