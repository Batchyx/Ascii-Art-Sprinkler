#!/bin/bash -eu

# Activate this script on the first two workdays
# if 1 is sunday, 2 is monday and 3 is tuesday
# if 2 is saterday, 2 is sunday, 3 is monday and 4 is tuesday
case "$(LC_ALL=C date +%a-%d-%m)" in
	*-0[12]-04);;
	Mon-0[23]-04);;
	Tue-0[34]-04);;
	*) exec cat;;
esac


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
fishy () {
	# FIXME: use 🐠🐟🐡🦈🐬🐳🐋
	case "$((RANDOM % 3))" in
	0) sed -re 's_$_ ><(((*>_';;
	1) sed -re 's_$_ <*)))‑{_';;
	2) sed -re 's_$_ 🐟_';;
	esac
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
