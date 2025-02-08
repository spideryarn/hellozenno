# from Jamie on WhatsApp AI prompts

echo "Branch: $(git rev-parse --abbrev-ref HEAD),\nDiff: $(git --no-pager diff)" | llm -t git-commit-msg ⁠
