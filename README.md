# Auxiom
auxiomai.com

## Description
This is the active repository for Auxiom AI. There are 3 main components: AWS Orchestration, Python Logic (Backend), and the Next.js webapp. 

## Quickstart
### General
1. Clone the repository to your local machine
2. Note the repository begins in `src`.
    - The backend (python) is in `src/service_tier/logic`
    - The webapp (nextjs) is in `src/webapp`
    - The AWS orchestration is in `src/service_tier` and `src/cron` depending on the stack you are working on
  
### Webapp
1. Navigate to `src/webapp`
2. Install node.js (which includes npm) if your node version is not up to date
3. Run `npm install` to install the dependencies locally
4. Run `npm run dev` to run a local instance of the auxiom webapp at `localhost:3000`
5. You can now modify components and see them change in real time!

### Backend (Python)
1. Navigate to `src/service_tier/logic`
2. Create a `if __name__ == '__main__'` section to test scripts locally

### AWS
For anything related to AWS, you will need to download the AWS CDK. If you are on windows, clone this repository to your WSL (since the CDK is for linux). Request credentials from rahilv99@gmail.com to set up your environment.

## Making Changes
1. Ensure the repo is cloned locally
2. Open a git bash terminal and navigate to the parent `/` directory (titled auxiom).
3. Type `git branch [branch name]`. You have created a new local branch. Name your branch after the feature you're creating.
4. Type `git checkout [branch name]`. You should now be on that branch.
5. Make your changes
6. Type `git push --set-upstream origin [branch name]`. You have now created a branch on the origin (remote) with the same name as your local branch.
7. Type `git add [file name]` to stage the changes from your specifed file. Type `git add .` to stage all changes.
8. Type `git commit -m [message]` with an informative message.
9. Type `git push` to push your changes to the remote instance of your branch.
10. The change has now created a pull request. Have one of the other contributors review and approve your pull request (or contact Rahil).
11. While you wait, you can switch back to the main branch with `git checkout main`. Your changes are pending approval so they are not yet reflected.
12. Once your changes are approved, type `git pull` to pull the changes from the remote branch. Do this frequently to stay up to date with everyone's changes.
13. Repeat the process for each new feature.

## Best Practices
1. ALWAYS branch when making a change. 
2. This is not for experimenting. Make a python notebook and transfer code once it is roughly functional.
