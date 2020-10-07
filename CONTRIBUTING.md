# How to Contribute

Contributions to this repo should be executed using the following steps:
- Clone this repo locally
    - Via ssh: `git clone git@github.com:skyebrownh/player-profile-dashboard.git`
    - Via https: `git clone https://github.com/skyebrownh/player-profile-dashboard.git`
    - Via GitHub CLI: `gh repo clone skyebrownh/player-profile-dashboard`
- Checkout the `dev` branch
    - `git checkout dev`
- Create a new branch from the `dev` branch (preferably named <your-name>_dev)
    - `git checkout -b <your-name>_dev`
- Make changes / commits
    - `git add . && git commit -m "<commit message>"`
- Push to your remote branch (not the `dev` branch)
    - `git push origin <your-name>_dev`
- Open a pull request to merge your branch into the `dev` branch
    - Via web:
        - Click Pull requests tab
        - Click New pull request
        - Give it a relevant and descriptive title
        - Select base: `dev`
        - Select compare: `<your_name>_dev`
        - Include any additional information about your changes in the body
        - Fix any initial conflicts
        - Request a code review
        - Link any relevant issues
        - Click Create pull request
    - Via GitHub CLI:
        - `gh pr create --base dev --title "Pull request title" --body "Pull request body"`
- Wait for your code to be reviewed and merged into the `dev` branch

