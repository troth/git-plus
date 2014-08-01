- MULTI: -q doesn't make sense for some of the commands

- MULTI: Parallelize all the git calls. This will require fairly
  intrusive changes to how git commands are executed.

- MULTI: Fix commits so that if you don't give a -F or -m on command
  line, the commit message is created for the first repo and reused
  for all repos.

- MULTI: Add man pages so 'git help multi' and 'git multi --help' will work.

- MULTI: Ability to specifiy a list of repos to work on.

- MULTI: Bad arguments cause stack trace.

  Example:

      $ git multi -p
      Traceback (most recent call last):
        File "/Users/junrue/bin/git-plus/git-multi", line 146, in <module>
          single_project = get_arg(args, 'p', 'project')
        File "/Users/junrue/bin/git-plus/git-multi", line 48, in get_arg
          result = args[i + 1]
      IndexError: list index out of range

- MULTI: Add feature to report which repos lack a branch.
  Show repos not on specified branch.
