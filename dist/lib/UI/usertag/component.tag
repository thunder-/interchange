UserTag component Order name
UserTag component addAttr
UserTag component Routine <<EOR
sub {
	my ($name, $opt) = @_;
	my $val;

	my $table = $opt->{table} || $::Variable->{UI_COMPONENT_TABLE} || 'component';
	my $db = ::database_exists_ref($table)
		or do {
			::logError("bad component table %s", $table);
			return undef;
		};

	$val = $::Variable->{$name} if defined $::Variable->{$name};
	$val = $Global::Variable->{$name} if defined $Global::Variable->{$name};
	unless ($db->record_exists($name)) {
		::logError("bad component %s, record does not exist in %s", $name, $table);
		return undef;
	}
	$val = $db->field($name, 'variable');

	if(! length($val) ) {
		my $base = $db->field($name, 'base')
			or do {
			::logError("bad component %s, no value, no base in %s", $name, $table);
			return undef;
			};
		# How to avoid endless loops?
		if($base eq $name) {
			::logError("endless loop prevented in component %s, base=name", $name);
			return undef;
		}
		$val = $Tag->component($base);
	}

	if(! $val and ! $opt->{update}) {
		::logError("bad component %s, record does not exist in %s", $name, $table);
		return undef;
	}

	return $val unless $opt->{update};

	$val = delete $::Scratch->{$name};

	if(! $val) {
		::logError("write component %s in table %s: no value in Scratch",
					$name,
					$table,
		);
		return undef;
	}

	# get those pesky LOW_TRAFFIC includes
	if( $val =~ m/^\s*\[include\s+.*\]\s*$/i ) {
		$val =~ s/\[include\s+/[file /i;
		$val =~ s/\s+file\s*=/ name=/i;
		$val = ::interpolate_html($val);
	}

	$db->set_field($name, 'variable', $val);
	if($opt->{setvar}) {
		my $dir = $opt->{dir}
				|| $::Variable->{UI_COMPONENT_DIR}
				|| 'config/variables';
		if(! -d $dir) {
			require File::Path;
			mkpath($dir) 
				or do {
					::logError("mkpath %s for components: %s", $dir, $@);
					return undef;
				};
		}
		open(COMPONENT, ">$dir/$name") 
			or do {
				::logError("create %s in component dir %s: %s", $name, $dir, $!);
				return undef;
			};
		print COMPONENT "Variable $name <<_EO_COMPONENT\n";
		print COMPONENT <<EOF;
[calc] \$C_stack = [] unless \$C_stack;
		push \@\$C_stack, \$Scratch->{ui_component} || '';
		\$Scratch->{ui_component} = q{$name}; return; [/calc]
EOF
		print COMPONENT $val;
		print COMPONENT qq{__UI_EDIT_LINK__[calc] \$Scratch->{ui_component} = pop \@\$C_stack; return; [/calc]};
		print COMPONENT "\n_EO_COMPONENT\n";
		close COMPONENT;
	}
	return $val unless $opt->{hide};
	return 1 if $opt->{status};
	return;
}
EOR