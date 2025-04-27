The changelog shows improvement in Hello Zenno over time:

`/changelog`

It highlights features and improvements that users will care about.

We use a table of contents, broken down by month, and then into themes within each month.

The changelog is loosely based on the Git commit history but it does not map one to one.
- A given Git commit might map to one row in the changelog.
- Or it might not feature in the changelog at all if it's not user-facing, or got reverted, or is otherwise irrelevant.
- Or you might see multiple commits on the same changelog line, because together they make up a single user-facing feature.
- Or the same commit may appear on multiple lines, because that single commit included multiple features.

Each changelog line should be at most a sentence or two describing things in a way that an end-user (rather than a developer) with some familiarity with Hello Zenno will be able to understand.

For a change to merit a changelog line, it should be fairly major, e.g. we certainly don't want to include tweaks to formatting.


## If you have been given already-generated data




## If you haven't been given already-generated data

To see info about the most recent Git commits, use e.g.:

```bash
git log --pretty=format:'COMMIT: %h%nAUTHOR: %an%nDATE:%ad%nMESSAGE:%n%s%n%b%nFILES:' --name-status --date=format:'%Y-%m-%d %H:%M:%S' -n 50
```

or without the files:

```bash
git log --pretty=format:'COMMIT: %h%nDATE:%ad%nMESSAGE:%n%s%n%b' --date=format:'%Y-%m-%d %H:%M:%S' > git_log.txt
```

When displaying the one or more Git SHAs for a changelog line, use superscript and display the first *7* characters.