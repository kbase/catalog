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
 


=head2 is_repo_registered

  $return = $obj->is_repo_registered($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectModuleParams
$return is a Catalog.boolean
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.SelectModuleParams
$return is a Catalog.boolean
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description



=back

=cut

 sub is_repo_registered
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function is_repo_registered (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to is_repo_registered:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'is_repo_registered');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.is_repo_registered",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'is_repo_registered',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method is_repo_registered",
					    status_line => $self->{client}->status_line,
					    method_name => 'is_repo_registered',
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
 


=head2 get_repo_last_timestamp

  $timestamp = $obj->get_repo_last_timestamp($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectModuleParams
$timestamp is an int
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.SelectModuleParams
$timestamp is an int
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description



=back

=cut

 sub get_repo_last_timestamp
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_repo_last_timestamp (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_repo_last_timestamp:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_repo_last_timestamp');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_repo_last_timestamp",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_repo_last_timestamp',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_repo_last_timestamp",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_repo_last_timestamp',
				       );
    }
}
 


=head2 list_module_names

  $return = $obj->list_module_names($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.ListReposParams
$return is a reference to a list where each element is a string
ListReposParams is a reference to a hash where the following keys are defined:
	with_disabled has a value which is a Catalog.boolean
boolean is an int

</pre>

=end html

=begin text

$params is a Catalog.ListReposParams
$return is a reference to a list where each element is a string
ListReposParams is a reference to a hash where the following keys are defined:
	with_disabled has a value which is a Catalog.boolean
boolean is an int


=end text

=item Description



=back

=cut

 sub list_module_names
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_module_names (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_module_names:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_module_names');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_module_names",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_module_names',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_module_names",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_module_names',
				       );
    }
}
 


=head2 get_repo_details

  $return = $obj->get_repo_details($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.HistoryRepoParams
$return is a Catalog.RepoDetails
HistoryRepoParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
RepoDetails is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	module_description has a value which is a string
	service_language has a value which is a string
	owners has a value which is a reference to a list where each element is a string
	readme has a value which is a string
	method_ids has a value which is a reference to a list where each element is a string
	widget_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a Catalog.HistoryRepoParams
$return is a Catalog.RepoDetails
HistoryRepoParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
RepoDetails is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	git_commit_hash has a value which is a string
	version has a value which is a string
	module_description has a value which is a string
	service_language has a value which is a string
	owners has a value which is a reference to a list where each element is a string
	readme has a value which is a string
	method_ids has a value which is a reference to a list where each element is a string
	widget_ids has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_repo_details
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_repo_details (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_repo_details:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_repo_details');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.get_repo_details",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_repo_details',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_repo_details",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_repo_details',
				       );
    }
}
 


=head2 list_repo_versions

  $versions = $obj->list_repo_versions($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a Catalog.SelectModuleParams
$versions is a reference to a list where each element is a Catalog.RepoVersion
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
RepoVersion is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	with_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

$params is a Catalog.SelectModuleParams
$versions is a reference to a list where each element is a Catalog.RepoVersion
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
RepoVersion is a reference to a hash where the following keys are defined:
	timestamp has a value which is an int
	git_commit_hash has a value which is a string
	with_disabled has a value which is a Catalog.boolean


=end text

=item Description



=back

=cut

 sub list_repo_versions
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_repo_versions (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_repo_versions:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_repo_versions');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "Catalog.list_repo_versions",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_repo_versions',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_repo_versions",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_repo_versions',
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
$params is a Catalog.SelectModuleParams
$state is a Catalog.ModuleState
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
ModuleState is a reference to a hash where the following keys are defined:
	active has a value which is a Catalog.boolean
	release_approval has a value which is a string
	review_message has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string

</pre>

=end html

=begin text

$params is a Catalog.SelectModuleParams
$state is a Catalog.ModuleState
SelectModuleParams is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	git_url has a value which is a string
	with_disabled has a value which is a Catalog.boolean
boolean is an int
ModuleState is a reference to a hash where the following keys are defined:
	active has a value which is a Catalog.boolean
	release_approval has a value which is a string
	review_message has a value which is a string
	registration has a value which is a string
	error_message has a value which is a string


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
                method_name => 'get_module_state',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method get_module_state",
            status_line => $self->{client}->status_line,
            method_name => 'get_module_state',
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



=head2 SelectModuleParams

=over 4



=item Description

Describes how to find module/repository details.
module_name - name of module defined in kbase.yaml file;
with_disabled - optional flag adding disabled repos (default value is false).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
with_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
with_disabled has a value which is a Catalog.boolean


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



=head2 ListReposParams

=over 4



=item Description

Describes how to filter repositories.
with_disabled - optional flag adding disabled repos (default value is false).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
with_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
with_disabled has a value which is a Catalog.boolean


=end text

=back



=head2 RepoDetails

=over 4



=item Description

method_ids - list of method ids (each id is fully qualified, i.e. contains module
    name prefix followed by slash);
widget_ids - list of widget ids (each id is name of JavaScript file stored in
    repo's 'ui/widgets' folder).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
git_commit_hash has a value which is a string
version has a value which is a string
module_description has a value which is a string
service_language has a value which is a string
owners has a value which is a reference to a list where each element is a string
readme has a value which is a string
method_ids has a value which is a reference to a list where each element is a string
widget_ids has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
git_url has a value which is a string
git_commit_hash has a value which is a string
version has a value which is a string
module_description has a value which is a string
service_language has a value which is a string
owners has a value which is a reference to a list where each element is a string
readme has a value which is a string
method_ids has a value which is a reference to a list where each element is a string
widget_ids has a value which is a reference to a list where each element is a string


=end text

=back



=head2 HistoryRepoParams

=over 4



=item Description

Describes how to find repository details (including old versions). In case neither of
    version and git_commit_hash is specified last version is returned.
module_name - name of module defined in kbase.yaml file;
timestamp - optional parameter limiting search by certain version timestamp;
git_commit_hash - optional parameter limiting search by certain git commit hash;
with_disabled - optional flag adding disabled repos (default value is false).


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
with_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
timestamp has a value which is an int
git_commit_hash has a value which is a string
with_disabled has a value which is a Catalog.boolean


=end text

=back



=head2 RepoVersion

=over 4



=item Description

timestamp will be epoch time


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
timestamp has a value which is an int
git_commit_hash has a value which is a string
with_disabled has a value which is a Catalog.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
timestamp has a value which is an int
git_commit_hash has a value which is a string
with_disabled has a value which is a Catalog.boolean


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
