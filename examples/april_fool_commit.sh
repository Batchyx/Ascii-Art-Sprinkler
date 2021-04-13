#!/bin/bash -eu

# This script can be inserted into a git multimail or git post-receive-email
# hook to spice it up on April the 1st and 2nd, or at least on the first two
# work days.
#
# It heavily depends on the 'filters' package
# https://joeyh.name/code/filters/
#
# It will:
# - Pass the beginning of the email through the 'spammer' filter.
# - Pass the commit message through a random selection of filters from the
#   'filters' package
# - Parse the patch and use the 'rasterman' filter on added lines, to add typos
#   on the changes.
# - Sprinkle ASCII Art of fishes over everything (this is a west-european
#   reference).
#
# To use it, edit the two variable below, and arrange this program to be called
# prior to sending the mail, either by configuring hook.sendmailcommand or by
# modifying the hook directly.

: "${SPRINKLE_ASCII_ART="/path/to/sprinkle-ascii-art.py"}"
: "${ART_FILE="/path/to/fishes.asciiart"}"

if [ -z "${FORCE_APRIL_FOOL:+set}" ]; then
	# Activate this script on the first two workdays
	# if 1 is sunday, 2 is monday and 3 is tuesday
	# if 2 is saterday, 2 is sunday, 3 is monday and 4 is tuesday
	case "$(LC_ALL=C date +%a-%d-%m)" in
		*-0[12]-04);;
		Mon-0[23]-04);;
		Tue-0[34]-04);;
		*) exec cat;;
	esac
fi


try () {
	if type "$1" > /dev/null 2>&1; then
		"$@"
	else
		cat
	fi
}

random_filter () {
	shift $((RANDOM%$#))
	try "$1"
}

try_turn_lowercase () {
	if type "$1" > /dev/null 2>&1; then
		"$1" | tr '[[:upper:]]' '[[:lower:]]'
	else
		cat
	fi
}
b1ff_lower () {
	try_turn_lowercase b1ff
}
lolcat_lower () {
	try_turn_lowercase LOLCAT
}

frobnicate_commit_msg () {
	# chef is too extreme, as in, unreadable
	# eleet is too visible ?
	# fudd is a bit hard to read
	# kenny is just unreadable
	# kraut isn't funny enough
	# nethackify not funny
	# newspeak does not change much
	# censor won't do much
	# scramble is sometimes hard
	# studly is stupid, uniencode not funny, upside-down could need more...
	random_filter b1ff_lower lolcat_lower cockney eleet jethro \
		jive ken kraut ky00te nyc pirate scottish scramble
}

frobnicate_patch () {
	local line IFS
	while IFS='' read -r line; do
		case "$line" in
		+*) 
			printf "%s\n" "$line" | \
				random_filter cat cat cat rasterman;;
		*)
			printf "%s\n" "$line";;
		esac
	done
}

frobnicate_end () {
	try rasterman
}

newline="
"
filter_all_until () {
	local text=""
	while IFS='' read -r LINE; do
		case "$LINE" in
			$1) break;;
		esac
		text="$text$LINE$newline"
	done
	shift
	"$@" << EOF
$text
EOF
}

# Don't touch email headers (even if we could, hum, frobnicate the subject...)
filter_all_until "" cat
printf "%s\n" "$LINE"

{
# fuck up the description that nobody reads.
filter_all_until "- Log ---*" spammer
printf "%s\n" "$LINE"


commitmsg=""
patchmsg=""
mode=""
oldmode=""
while IFS='' read -r LINE; do
	: "line: $LINE"
	case "$LINE" in
	"commit "*)
		mode="";;
	"    "*)
		mode="${mode:-commit}";;
	"diff --git "*)
		mode="patch";;
	"-----------------------------------------------------------------------")
		mode="end";;
	esac

	if [ "$oldmode" != "$mode" ]; then
		case "$oldmode" in
		commit) frobnicate_commit_msg << EOF
$commitmsg
EOF
			commitmsg="";;
		patch) frobnicate_patch << EOF
$patchmsg
EOF
			patchmsg="";;
		esac
	fi
	oldmode="$mode"

	case "$mode" in
	commit) commitmsg="$commitmsg${commitmsg:+$newline}$LINE";;
	patch) patchmsg="$patchmsg${patchmsg:+$newline}$LINE";;
	"") printf "%s\n" "$LINE";;
	end) printf "%s\n" "$LINE"; break;;
	esac
done
frobnicate_end
} | {
	# spammer may add \r for fun.  well, it can be funny, but not here.
	tr -d '\r'
} | {
	if type iconv > /dev/null 2>&1; then
		# mostly rasterman's fault
		iconv -c -f UTF-8 -t UTF-8 | "$SPRINKLE_ASCII_ART" "$ART_FILE"
	else
		cat
	fi
}
