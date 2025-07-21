# my-github-reviewer
Used to review PR's with the help of git workflows. 


Steps To Run This Using Git WorkFlows:


1.In .github/workflows    add a code-reviewer.yml file with below code

********************************************************************************


name: "PR Review with GPT on Comment"

on:
  issue_comment:
    types: [created]

permissions: write-all

jobs:
  review-pr:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/git-review')
    runs-on: ubuntu-latest

    steps:
      - name: Log PR Info
        run: |
          echo "PR Number: ${{ github.event.issue.number }}"
          echo "Repository: ${{ github.repository }}"
          echo "Comment: ${{ github.event.comment.body }}"

      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run GitHub Reviewer Action
        uses: Rakeshreddysr2401/my-github-reviewer@dev-llm-config
        with:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PULL_NUMBER: ${{ github.event.issue.number }}
          REPOSITORY: ${{ github.repository }}
          EXCLUDE: "*.md,*.txt,package-lock.json,*.yml,*.yaml"

**************************************************************************************

And in Github Secrets 
Add 
1.OPENAI_API_KEY = "sjhdkhd"   (if any other models used need to add accordingly)
2.GITHUB_TOKEN (No Need to add it takes by default)


To Run This Flow
Add a comment as  /git-review   then this flow will run



we can also add below keys to used other models of llm
by adding in below EXCLUDE key - value

PROVIDER="openai"
MODEL_NAME="gpt-4o"
TEMPERATURE="0.7"
