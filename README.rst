===================
ASCII Art Sprinkler
===================

::

                      *                               V      V
           *                 ASCII Art Sprinkler     >#<    >#<   *
                                                      |      |
                  *     *   *    *              *                                 *

    Take your plain text ASCII files to the next level ! This program will       |
    randomly sprinkle ASCII Art on your plain text, without destroying its      -#-
    content or format.                                                           |
                                  *
      *      *                                   *    *         *      *    *

    It takes its ASCII Art from a configuration file, reads standard input
    and randomly fills all the white space that naturally occurs in most
    text files.                                                            |
                    *                               *                     -#-    *
                      *          *                              *   *      |

    Some ASCII Art examples are provided, but of course, you can easily define
    your own ! Imagination is the only limit.                                  *
                                                  *       *  *
       *  *                  *                 *                       *  |   *
                                                        ==.              \|/
    See the examples below for what can be achieved.      -=_.       ...==#--  *
                                                             ""-==--"""  /|\
           ^                   |        |                                 |     |
        __/ \__               \|/      \|/  ___..==.__                         -#-
        \     /              --#--    ..#==---       -"=.                       |
         \   /   *            /|\      /|\              -==
         / . \                 |        |
        /.- -.\


-----
Usage
-----

This is a simple Python >= 3.7 script without any external dependency.
It requires a configuration file with the ASCII Art to sprinkle
(some examples are provided in `examples/ <examples/>`_.)
It reads stdin and write to stdout.

    $ ./ascii_art_sprinkler.py examples/stars.asciiart < your-text-file.txt

stdin does not have to be a file, this program supports infinite input
(try `yes "" | ./ascii_art_sprinkler.py examples/stars.asciiart` !)

Configuration files are very simple: Just put ASCII Art to sprinkle,
separated by a blank line::

     -----
    /  o  \
    \     |
     ---  /
     |   |

     -----
    d o_o b
     |   |
     | w |
     |___|

     /MMM\
    / ^ ^ \
    |  o  |
     |WWW|


More options can be specified in configuration files.  See
`examples/documentation.asciiart <examples/documentation.asciiart>`_.

----
Tips
----

Smaller ASCII Art works better against arbitrarily dense text files.
Otherwise, adding more whitespace is generally a good idea.


--------
Examples
--------

You already have seen the header above.  Here's more.

Why not make your *love letters* (aka PR) to your dear maintainers
`a bit more cute <https://www.reddit.com/r/ProgrammerHumor/comments/ll34yc/would_you_merge_with_them/>`_
? (Or degenerate, depending on your point of view).

::

                              >w<                 ^-^             UwU  ;;w;;
        Hii~~

        I fixie wixied the JSON-api fucksy wucksie!!! xpp                    :3

        I repwaced the `Prototypes.func` wiff a more ~streamylined~ kawaii
        `Pwototypiee.funkywunks` object that make the JS go sooper dooper fast!!
        XD *starts twerking*
                                                                    ## ##
        Can u pwease merge my pwull wequest senpai?!! UwU  :3      #######
                                                                    #####
                                                                     ###
                              x3       UwU                            #     OwO



With programming languages that supports inline comments, it is possible
to sprinkle ASCII Art in them.

And the code will still compile. `Unfortunately <https://www.schneier.com/blog/archives/2008/05/random_number_b.html>`_.


::

            EVP_MD_CTX_init(&m);                   /* very secure */
            for (i=0; i<num; i+=MD_DIGEST_LENGTH)
                    {                                  /* very unique key */
                    j=(num-i);
                    j=(j > MD_DIGEST_LENGTH)?MD_DIGEST_LENGTH:j;

                    MD_Init(&m);
                    MD_Update(&m,local_md,MD_DIGEST_LENGTH);  /* very unique key */
                    k=(st_idx+j)-STATE_SIZE;
                    if (k > 0)                                 /*  hyper safe  */
                            {
                            MD_Update(&m,&(state[st_idx]),j-k);
      /* safe 4 years */    MD_Update(&m,&(state[0]),k);
                            }                                   /* nsa-proof */
                    else
                            MD_Update(&m,&(state[st_idx]),j);
                                                                /* many purity */
    /*                                  /* valgrind agree */
     * Don't add uninitialised data.                          /* audit-approved */
                    MD_Update(&m,buf,j);
    */
                    MD_Update(&m,(unsigned char *)&(md_c[0]),sizeof(md_c));
                    MD_Final(&m,local_md);
                    md_c[1]++;                           /* so much wow */

                    buf=(const char *)buf + j;             /* good crypto */

                    for (k=0; k<j; k++)  /* very secure */    /* nsa-proof */
                            {
                            /* Parallel threads may interfere with this,
                             * but always each byte of the new state is
                             * the XOR of some previous value of its
     /* very zero CVE */     * and local_md (itermediate values may be lost).
                             * Alway using locking could hurt performance more
       /* safe 4 years */    * than necessary given that conflicts occur only
                             * when the total seeding is longer than the random
      /* can't do better */  * state. */
                            state[st_idx++]^=local_md[k];
                            if (st_idx >= STATE_SIZE)      /* so much wow */
                                    st_idx=0;
                            }
                    }                                         /* can't do better */
            EVP_MD_CTX_cleanup(&m);


-------
History
-------

This was originally made as part of an april fool joke.

It would take these boring email generated by git's post-receive-email hook::

    This is an automated email from the git hooks/post-receive script. It was
    generated because a ref change was pushed to the repository containing
    the project "Commit Screwdriver".

    The branch, main has been updated
           via  25d253e86d4248604f50761ae1e950b68050fb22 (commit)
          from  76907a33fb270d8fa99328357c90fd4041f7c733 (commit)

    Those revisions listed above that are new to this repository have
    not appeared on any other notification email; so we list those
    revisions in full, below.

    - Log -----------------------------------------------------------------
    commit 25d253e86d4248604f50761ae1e950b68050fb22
    Author: batchy <batchy@batchy>
    Date:   Mon Apr 2 22:14:02 2018 +0200

        rename screw_up_commit and try to fix bugs.

    diff --git a/screw_up_commit.sh b/april_fool_commit
    similarity index 92%
    rename from screw_up_commit.sh
    rename to april_fool_commit
    index 04cccf8..782c93e 100755
    --- a/screw_up_commit.sh
    +++ b/april_fool_commit
    @@ -98,6 +98,7 @@ EOF
     filter_all_until "" cat
     printf "%s\n" "$LINE"

    +{
     # fuck up the description that nobody reads.
     filter_all_until "- Log ---*" spammer
     printf "%s\n" "$LINE"
    @@ -142,3 +143,14 @@ EOF
        esac
     done
     frobnicate_end
    +} | {
    +   # spammer may add \r for fun.  well, it can be funny, but not here.
    +   tr -d '\r'
    +} | {
    +   if type iconv > /dev/null 2>&1; then
    +           # mostly rasterman's fault
    +           iconv -c -f UTF-8 -t UTF-8 | try fishy.py
    +   else
    +           cat
    +   fi
    +}

    -----------------------------------------------------------------------

    Summary of changes:
     screw_up_commit.sh => april_fool_commit | 12 ++++++++++++
     1 file changed, 12 insertions(+)
     rename screw_up_commit.sh => april_fool_commit (92%)


    hooks/post-receive
    --
    Commit Screwdriver



And would use a combination of text filters to spice it up before
adding a bunch of fishes (some european april fool tradition)::

    This is an automated email (sent in compliance with regulations) from the git hooks/post-receive script. VIAGRA! It was
    GENERATED BECAUSE A REF CHANGE WAS PUSHED TO THE REPOSITORY CONTAINING
    the project "Commit Screwdriver".
                                                                               ><>
    The branch, main has been updated                                <*)))><  ><>
           via  25d253e86d4248604f50761ae1e950b68050fb22 (commit)              ><>
          from  76907a33fb270d8fa99328357c90fd4041f7c733 (commit)

    Those revisions listed above that are new to this repository have
    not appeared on any other notification email (sent in compliance with regulations); so we list those
    revisions in 100% GUARANTEED, below.
    This is a one time offer.

    To be removed from future mailings to this mailing list reply with a subject of "remove"!

    - Log -----------------------------------------------------------------
    commit 25d253e86d4248604f50761ae1e950b68050fb22
    Author: batchy <batchy@batchy>
    Date:   Mon Apr 2 22:14:02 2018 +0200                        \             /
                                                               /--\           /\
        rrename scrrew_up_commeowt 'n trry ta fyx bugs.      <=  (o>         <'(=<
                                                               \--/           \/
    diff --git a/screw_up_commit.sh b/april_fool_commit          /             \
    similarity index 92%
    rename from screw_up_commit.sh
    rename to april_fool_commit
    index 04cccf8..782c93e 100755                              _///_
    --- a/screw_up_commit.sh                          <'><|   /o    \/
    +++b /april_ool_commit                   __               > ))_./\    ><((">
    @@ -98,6 +98,7 @@ EOF                  \/ o\                 <
     filter_all_until "" cat               /\__/       |><'>
     printf "%s\n" "$LINE"

    +{                                                   ,/..
     # fuck up the description that nobody reads.      <')   `=<
     filter_all_until "- Log ---*" spammer              ``\```
     printf "%s\n" "$LINE"
    @@ -142,3 +143,14 @@ EOF                                       ><((">
            esac                   ><(((*>
     done                                       <'><|  <'><|
     frobnicate_end
    +} | {
    +       # spammer may add \r for fun.  well.. it can be funny.. butr not here...
    +       tr -d '\r'
    +} | {
    +       if type iconv > /dev/null 2>&1; then
    +               # mostly rasterman's fault
    +               iucovn -c -f utf- -t utf-8 | try fishy.py
    +       else
    +               cat
    +       fi              |><((o>          <"))><                       <*)))><
    +}

    -----------------------------------------------------------------------
                                                                             <><
    summary of changes:                                                       <><
     screw_up_commitsh => aprilk_fool_comit | 12 ++++++++++++      ><>       <><
     1 filew changed.. 12 insertions(+)                           ><>
     rename screww_up_commit.sh => april_fool_cmmit (92%)          ><>


    hooks/post-receive         >°))))))))><<         <o))><|         |><((o>
    --
    commit screwdriver
