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
	include_modules_with_no_name_set has a value which is a Catalog.boolean
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
	include_modules_with_no_name_set has a value which is a Catalog.boolean
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
ListFavoriteCounts is a reference to a hash where the following keys are defined:
	modules has a value which is a reference to a list where each element is a string
FavoriteCount is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	app_id has a value which is a string
	count has a value which is an int

</pre>

=end html

=begin text

$params is a Catalog.ListFavoriteCounts
$counts is a reference to a list where each element is a Catalog.FavoriteCount
ListFavoriteCounts is a reference to a hash where the following keys are defined:
	modules has a value which is a reference to a list where each element is a string
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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean

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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean


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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean

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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean


=end text

=item Description

DEPRECATED!!!  use get_module_version

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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean

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
	dynamic_service has a value which is a Catalog.boolean
	narrative_method_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
boolean is an int
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean


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
 


=head2 get_module_version

  $version = $obj->get_module_version($selection)

=over 4

=item Parameter and return types

=begin html

<pre>
$selection is a Catalog.SelectModuleVersion
$version is a Catalog.ModuleVersion
SelectModuleVersion is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	version has a value which is a string
	include_module_description has a value which is a Catalog.boolean
	include_compilation_report has a value which is a Catalog.boolean
boolean is an int
ModuleVersion is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	module_description has a value which is a string
	git_url has a value which is a string
	released has a value which is a Catalog.boolean
	release_tags has a value which is a reference to a list where each element is a string
	timestamp has a value which is an int
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	dynamic_service has a value which is a Catalog.boolean
	narrative_app_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean

</pre>

=end html

=begin text

$selection is a Catalog.SelectModuleVersion
$version is a Catalog.ModuleVersion
SelectModuleVersion is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	version has a value which is a string
	include_module_description has a value which is a Catalog.boolean
	include_compilation_report has a value which is a Catalog.boolean
boolean is an int
ModuleVersion is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	module_description has a value which is a string
	git_url has a value which is a string
	released has a value which is a Catalog.boolean
	release_tags has a value which is a reference to a list where each element is a string
	timestamp has a value which is an int
	registration_id has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	git_commit_message has a value which is a string
	dynamic_service has a value which is a Catalog.boolean
	narrative_app_ids has a value which is a reference to a list where each element is a string
	local_function_ids has a value which is a reference to a list where each element is a string
	docker_img_name has a value which is a string
	data_folder has a value which is a string
	data_version has a value which is a string
	compilation_report has a value which is a Catalog.CompilationReport
CompilationReport is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	sdk_version has a value which is a string
	sdk_git_commit has a value which is a string
	impl_file_path has a value which is a string
	function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
	functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
	spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile
FunctionPlace is a reference to a hash where the following keys are defined:
	start_line has a value which is an int
	end_line has a value which is an int
Function is a reference to a hash where the following keys are defined:
	name has a value which is a string
	comment has a value which is a string
	place has a value which is a Catalog.FunctionPlace
	input has a value which is a reference to a list where each element is a Catalog.Parameter
	output has a value which is a reference to a list where each element is a Catalog.Parameter
Parameter is a reference to a hash where the following keys are defined:
	type has a value which is a string
	comment has a value which is a string
SpecFile is a reference to a hash where the following keys are defined:
	file_name has a value which is a string
	content has a value which is a string
	is_main has a value which is a Catalog.boolean


=end text

=item Description



=back

=cut

 sub get_module_version
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_module_version (received $n, expecting 1)");
    }
    {
	my($selection) = @args;

	my @_bad_arguments;
        (ref($selection) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"selection\" (value was \"$selection\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_module_version:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_module_version');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_module_version",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_module_version',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_module_version",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_module_version',
				       );
    }
}
 


=head2 list_local_functions

  $info_list = $obj->list_local_functions($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ListLocalFunctionParams
$info_list is a reference to a list where each element is a Catalog.LocalFunctionInfo
ListLocalFunctionParams is a reference to a hash where the following keys are defined:
	release_tag has a value which is a string
	module_names has a value which is a reference to a list where each element is a string
LocalFunctionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	release_tag has a value which is a reference to a list where each element is a string
	name has a value which is a string
	short_description has a value which is a string
	tags has a value which is a Catalog.LocalFunctionTags
LocalFunctionTags is a reference to a hash where the following keys are defined:
	categories has a value which is a reference to a list where each element is a string
	input has a value which is a Catalog.IOTags
	output has a value which is a Catalog.IOTags
IOTags is a reference to a hash where the following keys are defined:
	file_types has a value which is a reference to a list where each element is a string
	kb_types has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.ListLocalFunctionParams
$info_list is a reference to a list where each element is a Catalog.LocalFunctionInfo
ListLocalFunctionParams is a reference to a hash where the following keys are defined:
	release_tag has a value which is a string
	module_names has a value which is a reference to a list where each element is a string
LocalFunctionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	release_tag has a value which is a reference to a list where each element is a string
	name has a value which is a string
	short_description has a value which is a string
	tags has a value which is a Catalog.LocalFunctionTags
LocalFunctionTags is a reference to a hash where the following keys are defined:
	categories has a value which is a reference to a list where each element is a string
	input has a value which is a Catalog.IOTags
	output has a value which is a Catalog.IOTags
IOTags is a reference to a hash where the following keys are defined:
	file_types has a value which is a reference to a list where each element is a string
	kb_types has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub list_local_functions
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_local_functions (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_local_functions:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_local_functions');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_local_functions",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_local_functions',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_local_functions",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_local_functions',
				       );
    }
}
 


=head2 get_local_function_details

  $detail_list = $obj->get_local_function_details($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.GetLocalFunctionDetails
$detail_list is a reference to a list where each element is a Catalog.LocalFunctionDetails
GetLocalFunctionDetails is a reference to a hash where the following keys are defined:
	functions has a value which is a reference to a list where each element is a Catalog.SelectOneLocalFunction
SelectOneLocalFunction is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	release_tag has a value which is a string
	git_commit_hash has a value which is a string
LocalFunctionDetails is a reference to a hash where the following keys are defined:
	info has a value which is a Catalog.LocalFunctionInfo
	long_description has a value which is a string
LocalFunctionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	release_tag has a value which is a reference to a list where each element is a string
	name has a value which is a string
	short_description has a value which is a string
	tags has a value which is a Catalog.LocalFunctionTags
LocalFunctionTags is a reference to a hash where the following keys are defined:
	categories has a value which is a reference to a list where each element is a string
	input has a value which is a Catalog.IOTags
	output has a value which is a Catalog.IOTags
IOTags is a reference to a hash where the following keys are defined:
	file_types has a value which is a reference to a list where each element is a string
	kb_types has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.GetLocalFunctionDetails
$detail_list is a reference to a list where each element is a Catalog.LocalFunctionDetails
GetLocalFunctionDetails is a reference to a hash where the following keys are defined:
	functions has a value which is a reference to a list where each element is a Catalog.SelectOneLocalFunction
SelectOneLocalFunction is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	release_tag has a value which is a string
	git_commit_hash has a value which is a string
LocalFunctionDetails is a reference to a hash where the following keys are defined:
	info has a value which is a Catalog.LocalFunctionInfo
	long_description has a value which is a string
LocalFunctionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_id has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	release_tag has a value which is a reference to a list where each element is a string
	name has a value which is a string
	short_description has a value which is a string
	tags has a value which is a Catalog.LocalFunctionTags
LocalFunctionTags is a reference to a hash where the following keys are defined:
	categories has a value which is a reference to a list where each element is a string
	input has a value which is a Catalog.IOTags
	output has a value which is a Catalog.IOTags
IOTags is a reference to a hash where the following keys are defined:
	file_types has a value which is a reference to a list where each element is a string
	kb_types has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_local_function_details
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_local_function_details (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_local_function_details:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_local_function_details');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_local_function_details",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_local_function_details',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_local_function_details",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_local_function_details',
				       );
    }
}
 


=head2 module_version_lookup

  $return = $obj->module_version_lookup($selection)

=over 4

=item Parameter and return types

=begin html

<pre>
$selection is a Catalog.ModuleVersionLookupParams
$return is a Catalog.BasicModuleVersionInfo
ModuleVersionLookupParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	lookup has a value which is a string
	only_service_versions has a value which is a Catalog.boolean
boolean is an int
BasicModuleVersionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	docker_img_name has a value which is a string

</pre>

=end html

=begin text

$selection is a Catalog.ModuleVersionLookupParams
$return is a Catalog.BasicModuleVersionInfo
ModuleVersionLookupParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	lookup has a value which is a string
	only_service_versions has a value which is a Catalog.boolean
boolean is an int
BasicModuleVersionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	docker_img_name has a value which is a string


=end text

=item Description



=back

=cut

 sub module_version_lookup
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function module_version_lookup (received $n, expecting 1)");
    }
    {
	my($selection) = @args;

	my @_bad_arguments;
        (ref($selection) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"selection\" (value was \"$selection\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to module_version_lookup:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'module_version_lookup');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.module_version_lookup",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'module_version_lookup',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method module_version_lookup",
					    status_line => $self->{client}->status_line,
					    method_name => 'module_version_lookup',
				       );
    }
}
 


=head2 list_service_modules

  $service_modules = $obj->list_service_modules($filter)

=over 4

=item Parameter and return types

=begin html

<pre>
$filter is a Catalog.ListServiceModuleParams
$service_modules is a reference to a list where each element is a Catalog.BasicModuleVersionInfo
ListServiceModuleParams is a reference to a hash where the following keys are defined:
	tag has a value which is a string
BasicModuleVersionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	docker_img_name has a value which is a string

</pre>

=end html

=begin text

$filter is a Catalog.ListServiceModuleParams
$service_modules is a reference to a list where each element is a Catalog.BasicModuleVersionInfo
ListServiceModuleParams is a reference to a hash where the following keys are defined:
	tag has a value which is a string
BasicModuleVersionInfo is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	docker_img_name has a value which is a string


=end text

=item Description



=back

=cut

 sub list_service_modules
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_service_modules (received $n, expecting 1)");
    }
    {
	my($filter) = @args;

	my @_bad_arguments;
        (ref($filter) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"filter\" (value was \"$filter\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_service_modules:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_service_modules');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_service_modules",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_service_modules',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_service_modules",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_service_modules',
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
 


=head2 log_exec_stats

  $obj->log_exec_stats($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.LogExecStatsParams
LogExecStatsParams is a reference to a hash where the following keys are defined:
	user_id has a value which is a string
	app_module_name has a value which is a string
	app_id has a value which is a string
	func_module_name has a value which is a string
	func_name has a value which is a string
	git_commit_hash has a value which is a string
	creation_time has a value which is a float
	exec_start_time has a value which is a float
	finish_time has a value which is a float
	is_error has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.LogExecStatsParams
LogExecStatsParams is a reference to a hash where the following keys are defined:
	user_id has a value which is a string
	app_module_name has a value which is a string
	app_id has a value which is a string
	func_module_name has a value which is a string
	func_name has a value which is a string
	git_commit_hash has a value which is a string
	creation_time has a value which is a float
	exec_start_time has a value which is a float
	finish_time has a value which is a float
	is_error has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description

Request from Execution Engine for adding statistics about each method run. It could be done
using catalog admin credentials only.

=back

=cut

 sub log_exec_stats
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function log_exec_stats (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to log_exec_stats:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'log_exec_stats');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.log_exec_stats",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'log_exec_stats',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method log_exec_stats",
					    status_line => $self->{client}->status_line,
					    method_name => 'log_exec_stats',
				       );
    }
}
 


=head2 get_exec_aggr_stats

  $return = $obj->get_exec_aggr_stats($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.GetExecAggrStatsParams
$return is a reference to a list where each element is a Catalog.ExecAggrStats
GetExecAggrStatsParams is a reference to a hash where the following keys are defined:
	full_app_ids has a value which is a reference to a list where each element is a string
	per_week has a value which is a Catalog.boolean
boolean is an int
ExecAggrStats is a reference to a hash where the following keys are defined:
	full_app_id has a value which is a string
	time_range has a value which is a string
	number_of_calls has a value which is an int
	number_of_errors has a value which is an int
	total_queue_time has a value which is a float
	total_exec_time has a value which is a float

</pre>

=end html

=begin text

$params is a Catalog.GetExecAggrStatsParams
$return is a reference to a list where each element is a Catalog.ExecAggrStats
GetExecAggrStatsParams is a reference to a hash where the following keys are defined:
	full_app_ids has a value which is a reference to a list where each element is a string
	per_week has a value which is a Catalog.boolean
boolean is an int
ExecAggrStats is a reference to a hash where the following keys are defined:
	full_app_id has a value which is a string
	time_range has a value which is a string
	number_of_calls has a value which is an int
	number_of_errors has a value which is an int
	total_queue_time has a value which is a float
	total_exec_time has a value which is a float


=end text

=item Description



=back

=cut

 sub get_exec_aggr_stats
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_exec_aggr_stats (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_exec_aggr_stats:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_exec_aggr_stats');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_exec_aggr_stats",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_exec_aggr_stats',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_exec_aggr_stats",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_exec_aggr_stats',
				       );
    }
}
 


=head2 get_exec_aggr_table

  $table = $obj->get_exec_aggr_table($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ExecAggrTableParams
$table is an UnspecifiedObject, which can hold any non-null object
ExecAggrTableParams is a reference to a hash where the following keys are defined:
	begin has a value which is an int
	end has a value which is an int

</pre>

=end html

=begin text

$params is a Catalog.ExecAggrTableParams
$table is an UnspecifiedObject, which can hold any non-null object
ExecAggrTableParams is a reference to a hash where the following keys are defined:
	begin has a value which is an int
	end has a value which is an int


=end text

=item Description



=back

=cut

 sub get_exec_aggr_table
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_exec_aggr_table (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_exec_aggr_table:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_exec_aggr_table');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_exec_aggr_table",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_exec_aggr_table',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_exec_aggr_table",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_exec_aggr_table',
				       );
    }
}
 


=head2 get_exec_raw_stats

  $records = $obj->get_exec_raw_stats($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.GetExecRawStatsParams
$records is a reference to a list where each element is an UnspecifiedObject, which can hold any non-null object
GetExecRawStatsParams is a reference to a hash where the following keys are defined:
	begin has a value which is an int
	end has a value which is an int

</pre>

=end html

=begin text

$params is a Catalog.GetExecRawStatsParams
$records is a reference to a list where each element is an UnspecifiedObject, which can hold any non-null object
GetExecRawStatsParams is a reference to a hash where the following keys are defined:
	begin has a value which is an int
	end has a value which is an int


=end text

=item Description



=back

=cut

 sub get_exec_raw_stats
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_exec_raw_stats (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_exec_raw_stats:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_exec_raw_stats');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_exec_raw_stats",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_exec_raw_stats',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_exec_raw_stats",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_exec_raw_stats',
				       );
    }
}
 


=head2 set_client_group

  $obj->set_client_group($group)

=over 4

=item Parameter and return types

=begin html

<pre>
$group is a Catalog.AppClientGroup
AppClientGroup is a reference to a hash where the following keys are defined:
	app_id has a value which is a string
	client_groups has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$group is a Catalog.AppClientGroup
AppClientGroup is a reference to a hash where the following keys are defined:
	app_id has a value which is a string
	client_groups has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub set_client_group
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function set_client_group (received $n, expecting 1)");
    }
    {
	my($group) = @args;

	my @_bad_arguments;
        (ref($group) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"group\" (value was \"$group\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to set_client_group:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'set_client_group');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.set_client_group",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'set_client_group',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method set_client_group",
					    status_line => $self->{client}->status_line,
					    method_name => 'set_client_group',
				       );
    }
}
 


=head2 get_client_groups

  $groups = $obj->get_client_groups($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.GetClientGroupParams
$groups is a reference to a list where each element is a Catalog.AppClientGroup
GetClientGroupParams is a reference to a hash where the following keys are defined:
	app_ids has a value which is a reference to a list where each element is a string
AppClientGroup is a reference to a hash where the following keys are defined:
	app_id has a value which is a string
	client_groups has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.GetClientGroupParams
$groups is a reference to a list where each element is a Catalog.AppClientGroup
GetClientGroupParams is a reference to a hash where the following keys are defined:
	app_ids has a value which is a reference to a list where each element is a string
AppClientGroup is a reference to a hash where the following keys are defined:
	app_id has a value which is a string
	client_groups has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_client_groups
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_client_groups (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_client_groups:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_client_groups');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_client_groups",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_client_groups',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_client_groups",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_client_groups',
				       );
    }
}
 


=head2 set_volume_mount

  $obj->set_volume_mount($config)

=over 4

=item Parameter and return types

=begin html

<pre>
$config is a Catalog.VolumeMountConfig
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$config is a Catalog.VolumeMountConfig
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description

must specify all properties of the VolumeMountConfig

=back

=cut

 sub set_volume_mount
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function set_volume_mount (received $n, expecting 1)");
    }
    {
	my($config) = @args;

	my @_bad_arguments;
        (ref($config) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"config\" (value was \"$config\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to set_volume_mount:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'set_volume_mount');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.set_volume_mount",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'set_volume_mount',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method set_volume_mount",
					    status_line => $self->{client}->status_line,
					    method_name => 'set_volume_mount',
				       );
    }
}
 


=head2 remove_volume_mount

  $obj->remove_volume_mount($config)

=over 4

=item Parameter and return types

=begin html

<pre>
$config is a Catalog.VolumeMountConfig
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$config is a Catalog.VolumeMountConfig
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description

must specify module_name, function_name, client_group and this method will delete any configured mounts

=back

=cut

 sub remove_volume_mount
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function remove_volume_mount (received $n, expecting 1)");
    }
    {
	my($config) = @args;

	my @_bad_arguments;
        (ref($config) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"config\" (value was \"$config\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to remove_volume_mount:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'remove_volume_mount');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.remove_volume_mount",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'remove_volume_mount',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return;
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method remove_volume_mount",
					    status_line => $self->{client}->status_line,
					    method_name => 'remove_volume_mount',
				       );
    }
}
 


=head2 list_volume_mounts

  $volume_mount_configs = $obj->list_volume_mounts($filter)

=over 4

=item Parameter and return types

=begin html

<pre>
$filter is a Catalog.VolumeMountFilter
$volume_mount_configs is a reference to a list where each element is a Catalog.VolumeMountConfig
VolumeMountFilter is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$filter is a Catalog.VolumeMountFilter
$volume_mount_configs is a reference to a list where each element is a Catalog.VolumeMountConfig
VolumeMountFilter is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
VolumeMountConfig is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	function_name has a value which is a string
	client_group has a value which is a string
	volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount
VolumeMount is a reference to a hash where the following keys are defined:
	host_dir has a value which is a string
	container_dir has a value which is a string
	read_only has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description



=back

=cut

 sub list_volume_mounts
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_volume_mounts (received $n, expecting 1)");
    }
    {
	my($filter) = @args;

	my @_bad_arguments;
        (ref($filter) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"filter\" (value was \"$filter\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_volume_mounts:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_volume_mounts');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_volume_mounts",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_volume_mounts',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_volume_mounts",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_volume_mounts',
				       );
    }
}
 


=head2 is_admin

  $return = $obj->is_admin($username)

=over 4

=item Parameter and return types

=begin html

<pre>
$username is a string
$return is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$username is a string
$return is a Catalog.boolean
boolean is an int


=end text

=item Description

returns true (1) if the user is an admin, false (0) otherwise

=back

=cut

 sub is_admin
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function is_admin (received $n, expecting 1)");
    }
    {
	my($username) = @args;

	my @_bad_arguments;
        (!ref($username)) or push(@_bad_arguments, "Invalid type for argument 1 \"username\" (value was \"$username\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to is_admin:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'is_admin');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.is_admin",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'is_admin',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method is_admin",
					    status_line => $self->{client}->status_line,
					    method_name => 'is_admin',
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
                method_name => 'is_admin',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method is_admin",
            status_line => $self->{client}->status_line,
            method_name => 'is_admin',
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



=head2 ListModuleParams

=over 4



=item Description

Describes how to filter repositories.
include_released - optional flag indicated modules that are released are included (default:true)
include_unreleased - optional flag indicated modules that are not released are included (default:false)
with_disabled - optional flag indicating disabled repos should be included (default:false).
include_modules_with_no_name_set - default to 0, if set return modules that were never
                                    registered successfully (first registration failed, never
                                    got a module name, but there is a git_url)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
owners has a value which is a reference to a list where each element is a string
include_released has a value which is a Catalog.boolean
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean
include_modules_with_no_name_set has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
owners has a value which is a reference to a list where each element is a string
include_released has a value which is a Catalog.boolean
include_unreleased has a value which is a Catalog.boolean
include_disabled has a value which is a Catalog.boolean
include_modules_with_no_name_set has a value which is a Catalog.boolean


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


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
modules has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
modules has a value which is a reference to a list where each element is a string


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



=head2 FunctionPlace

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
start_line has a value which is an int
end_line has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
start_line has a value which is an int
end_line has a value which is an int


=end text

=back



=head2 Parameter

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
type has a value which is a string
comment has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
type has a value which is a string
comment has a value which is a string


=end text

=back



=head2 Function

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
name has a value which is a string
comment has a value which is a string
place has a value which is a Catalog.FunctionPlace
input has a value which is a reference to a list where each element is a Catalog.Parameter
output has a value which is a reference to a list where each element is a Catalog.Parameter

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
name has a value which is a string
comment has a value which is a string
place has a value which is a Catalog.FunctionPlace
input has a value which is a reference to a list where each element is a Catalog.Parameter
output has a value which is a reference to a list where each element is a Catalog.Parameter


=end text

=back



=head2 SpecFile

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
file_name has a value which is a string
content has a value which is a string
is_main has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
file_name has a value which is a string
content has a value which is a string
is_main has a value which is a Catalog.boolean


=end text

=back



=head2 CompilationReport

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
sdk_version has a value which is a string
sdk_git_commit has a value which is a string
impl_file_path has a value which is a string
function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
sdk_version has a value which is a string
sdk_git_commit has a value which is a string
impl_file_path has a value which is a string
function_places has a value which is a reference to a hash where the key is a string and the value is a Catalog.FunctionPlace
functions has a value which is a reference to a hash where the key is a string and the value is a Catalog.Function
spec_files has a value which is a reference to a list where each element is a Catalog.SpecFile


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
dynamic_service has a value which is a Catalog.boolean
narrative_method_ids has a value which is a reference to a list where each element is a string
local_function_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string
compilation_report has a value which is a Catalog.CompilationReport

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
timestamp has a value which is an int
registration_id has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
dynamic_service has a value which is a Catalog.boolean
narrative_method_ids has a value which is a reference to a list where each element is a string
local_function_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string
compilation_report has a value which is a Catalog.CompilationReport


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



=head2 ModuleVersion

=over 4



=item Description

module_name            - the name of the module
module_description     - (optionally returned) html description in KBase YAML of this module
git_url                - the git url of the source for this module

released               - 1 if this version has been released, 0 otherwise
release_tags           - list of strings of: 'dev', 'beta', or 'release', or empty list
                         this is a list because the same commit version may be the version in multiple release states
release_timestamp      - time in ms since epoch when this module was approved and moved to release, null otherwise
                         note that a module was released before v1.0.0, the release timestamp may not have been
                         recorded and will default to the registration timestamp

timestamp              - time in ms since epoch when the registration for this version was started
registration_id        - id of the last registration for this version, used for fetching registration logs and state

version                - validated semantic version number as indicated in the KBase YAML of this version
                         semantic versions are unique among released versions of this module

git_commit_hash        - the full git commit hash of the source for this module
git_commit_message     - the message attached to this git commit

dynamic_service        - 1 if this version is available as a web service, 0 otherwise

narrative_app_ids      - list of Narrative App ids registered with this module version
local_function_ids     - list of Local Function ids registered with this module version

docker_img_name        - name of the docker image for this module created on registration
data_folder            - name of the data folder used 

compilation_report     - (optionally returned) summary of the KIDL specification compilation


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
module_description has a value which is a string
git_url has a value which is a string
released has a value which is a Catalog.boolean
release_tags has a value which is a reference to a list where each element is a string
timestamp has a value which is an int
registration_id has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
dynamic_service has a value which is a Catalog.boolean
narrative_app_ids has a value which is a reference to a list where each element is a string
local_function_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string
compilation_report has a value which is a Catalog.CompilationReport

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
module_description has a value which is a string
git_url has a value which is a string
released has a value which is a Catalog.boolean
release_tags has a value which is a reference to a list where each element is a string
timestamp has a value which is an int
registration_id has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
git_commit_message has a value which is a string
dynamic_service has a value which is a Catalog.boolean
narrative_app_ids has a value which is a reference to a list where each element is a string
local_function_ids has a value which is a reference to a list where each element is a string
docker_img_name has a value which is a string
data_folder has a value which is a string
data_version has a value which is a string
compilation_report has a value which is a Catalog.CompilationReport


=end text

=back



=head2 SelectModuleVersion

=over 4



=item Description

Get a specific module version.

Requires either a module_name or git_url.  If both are provided, they both must match.

If no other options are specified, then the latest 'release' version is returned.  If
the module has not been released, then the latest 'beta' or 'dev' version is returned.
You can check in the returned object if the version has been released (see is_released)
and what release tags are pointing to this version (see release_tags).

Optionally, a 'version' parameter can be provided that can be either:
    1) release tag: 'dev' | 'beta' | 'release'

    2) specific semantic version of a released version (you cannot pull dev/beta or other
       unreleased versions by semantic version)
        - e.g. 2.0.1

    3) semantic version requirement specification, see: https://pypi.python.org/pypi/semantic_version/
       which will return the latest released version that matches the criteria.  You cannot pull
       dev/beta or other unreleased versions this way.
        - e.g.:
            - '>1.0.0'
            - '>=2.1.1,<3.3.0'
            - '!=0.2.4-alpha,<0.3.0'

    4) specific full git commit hash

include_module_description - set to 1 to include the module description in the YAML file of this version;
                             default is 0
include_compilation_report - set to 1 to include the module compilation report, default is 0


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
version has a value which is a string
include_module_description has a value which is a Catalog.boolean
include_compilation_report has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
version has a value which is a string
include_module_description has a value which is a Catalog.boolean
include_compilation_report has a value which is a Catalog.boolean


=end text

=back



=head2 IOTags

=over 4



=item Description

Local Function Listing Support


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
file_types has a value which is a reference to a list where each element is a string
kb_types has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
file_types has a value which is a reference to a list where each element is a string
kb_types has a value which is a reference to a list where each element is a string


=end text

=back



=head2 LocalFunctionTags

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
categories has a value which is a reference to a list where each element is a string
input has a value which is a Catalog.IOTags
output has a value which is a Catalog.IOTags

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
categories has a value which is a reference to a list where each element is a string
input has a value which is a Catalog.IOTags
output has a value which is a Catalog.IOTags


=end text

=back



=head2 LocalFunctionInfo

=over 4



=item Description

todo: switch release_tag to release_tags


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_id has a value which is a string
git_commit_hash has a value which is a string
version has a value which is a string
release_tag has a value which is a reference to a list where each element is a string
name has a value which is a string
short_description has a value which is a string
tags has a value which is a Catalog.LocalFunctionTags

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_id has a value which is a string
git_commit_hash has a value which is a string
version has a value which is a string
release_tag has a value which is a reference to a list where each element is a string
name has a value which is a string
short_description has a value which is a string
tags has a value which is a Catalog.LocalFunctionTags


=end text

=back



=head2 LocalFunctionDetails

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
info has a value which is a Catalog.LocalFunctionInfo
long_description has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
info has a value which is a Catalog.LocalFunctionInfo
long_description has a value which is a string


=end text

=back



=head2 ListLocalFunctionParams

=over 4



=item Description

Allows various ways to filter.
Release tag = dev/beta/release, default is release
module_names = only include modules in the list; if empty or not
               provided then include everything


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
release_tag has a value which is a string
module_names has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
release_tag has a value which is a string
module_names has a value which is a reference to a list where each element is a string


=end text

=back



=head2 SelectOneLocalFunction

=over 4



=item Description

release_tag = dev | beta | release, if it doesn't exist and git_commit_hash isn't set, we default to release
              and will not return anything if the function is not released


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_id has a value which is a string
release_tag has a value which is a string
git_commit_hash has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_id has a value which is a string
release_tag has a value which is a string
git_commit_hash has a value which is a string


=end text

=back



=head2 GetLocalFunctionDetails

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
functions has a value which is a reference to a list where each element is a Catalog.SelectOneLocalFunction

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
functions has a value which is a reference to a list where each element is a Catalog.SelectOneLocalFunction


=end text

=back



=head2 BasicModuleVersionInfo

=over 4



=item Description

DYNAMIC SERVICES SUPPORT Methods


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
docker_img_name has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
docker_img_name has a value which is a string


=end text

=back



=head2 ModuleVersionLookupParams

=over 4



=item Description

module_name - required for module lookup
lookup - a lookup string, if empty will get the latest released module
            1) version tag = dev | beta | release
            2) semantic version match identifiier
            not supported yet: 3) exact commit hash
            not supported yet: 4) exact timestamp
only_service_versions - 1/0, default is 1


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
lookup has a value which is a string
only_service_versions has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
lookup has a value which is a string
only_service_versions has a value which is a Catalog.boolean


=end text

=back



=head2 ListServiceModuleParams

=over 4



=item Description

tag = dev | beta | release
if tag is not set, all release versions are returned


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
tag has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
tag has a value which is a string


=end text

=back



=head2 SetRegistrationStateParams

=over 4



=item Description

End Dynamic Services Support Methods


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



=head2 LogExecStatsParams

=over 4



=item Description

user_id - GlobusOnline login of invoker,
app_module_name - optional module name of registered repo (could be absent of null for
    old fashioned services) where app_id comes from,
app_id - optional method-spec id without module_name prefix (could be absent or null
    in case original execution was started through API call without app ID defined),
func_module_name - optional module name of registered repo (could be absent of null for
    old fashioned services) where func_name comes from,
func_name - name of function in KIDL-spec without module_name prefix,
git_commit_hash - optional service version (in case of dynamically registered repo),
creation_time, exec_start_time and finish_time - defined in seconds since Epoch (POSIX),
is_error - indicates whether execution was finished with error or not.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
user_id has a value which is a string
app_module_name has a value which is a string
app_id has a value which is a string
func_module_name has a value which is a string
func_name has a value which is a string
git_commit_hash has a value which is a string
creation_time has a value which is a float
exec_start_time has a value which is a float
finish_time has a value which is a float
is_error has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
user_id has a value which is a string
app_module_name has a value which is a string
app_id has a value which is a string
func_module_name has a value which is a string
func_name has a value which is a string
git_commit_hash has a value which is a string
creation_time has a value which is a float
exec_start_time has a value which is a float
finish_time has a value which is a float
is_error has a value which is a Catalog.boolean


=end text

=back



=head2 GetExecAggrStatsParams

=over 4



=item Description

full_app_ids - list of fully qualified app IDs (including module_name prefix followed by
    slash in case of dynamically registered repo).
per_week - optional flag switching results to weekly data rather than one row per app for 
    all time (default value is false)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
full_app_ids has a value which is a reference to a list where each element is a string
per_week has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
full_app_ids has a value which is a reference to a list where each element is a string
per_week has a value which is a Catalog.boolean


=end text

=back



=head2 ExecAggrStats

=over 4



=item Description

full_app_id - optional fully qualified method-spec id including module_name prefix followed
    by slash in case of dynamically registered repo (it could be absent or null in case
    original execution was started through API call without app ID defined),
time_range - one of supported time ranges (currently it could be either '*' for all time
    or ISO-encoded week like "2016-W01")
total_queue_time - summarized time difference between exec_start_time and creation_time moments
    defined in seconds since Epoch (POSIX),
total_exec_time - summarized time difference between finish_time and exec_start_time moments 
    defined in seconds since Epoch (POSIX).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
full_app_id has a value which is a string
time_range has a value which is a string
number_of_calls has a value which is an int
number_of_errors has a value which is an int
total_queue_time has a value which is a float
total_exec_time has a value which is a float

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
full_app_id has a value which is a string
time_range has a value which is a string
number_of_calls has a value which is an int
number_of_errors has a value which is an int
total_queue_time has a value which is a float
total_exec_time has a value which is a float


=end text

=back



=head2 ExecAggrTableParams

=over 4



=item Description

Get aggregated usage metrics; available only to Admins.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
begin has a value which is an int
end has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
begin has a value which is an int
end has a value which is an int


=end text

=back



=head2 GetExecRawStatsParams

=over 4



=item Description

Get raw usage metrics; available only to Admins.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
begin has a value which is an int
end has a value which is an int

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
begin has a value which is an int
end has a value which is an int


=end text

=back



=head2 AppClientGroup

=over 4



=item Description

app_id = full app id; if module name is used it will be case insensitive 
this will overwrite all existing client groups (it won't just push what's on the list)
If client_groups is empty or set to null, then the client_group mapping will be removed.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
app_id has a value which is a string
client_groups has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
app_id has a value which is a string
client_groups has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetClientGroupParams

=over 4



=item Description

if app_ids is empty or null, all client groups are returned


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
app_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
app_ids has a value which is a reference to a list where each element is a string


=end text

=back



=head2 VolumeMount

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
host_dir has a value which is a string
container_dir has a value which is a string
read_only has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
host_dir has a value which is a string
container_dir has a value which is a string
read_only has a value which is a Catalog.boolean


=end text

=back



=head2 VolumeMountConfig

=over 4



=item Description

for a module, function, and client group, set mount configurations


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_name has a value which is a string
client_group has a value which is a string
volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_name has a value which is a string
client_group has a value which is a string
volume_mounts has a value which is a reference to a list where each element is a Catalog.VolumeMount


=end text

=back



=head2 VolumeMountFilter

=over 4



=item Description

Parameters for listing VolumeMountConfigs.  If nothing is set, everything is
returned.  Otherwise, will return everything that matches all fields set.  For
instance, if only module_name is set, will return everything for that module.  If
they are all set, will return the specific module/app/client group config.  Returns
nothing if no matches are found.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_name has a value which is a string
client_group has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
function_name has a value which is a string
client_group has a value which is a string


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
