# Verbose Adventure

This is demo project for GPT interactive story generation.

## System Flow Diagram

```mermaid
flowchart LR
    subgraph "Initialize story (init_story)"
        startStory[Start story w/ API]
        initSys[(System message\nStart message)]
        saveMessage1[(Chatcmpl & Choice\nMessage)]
    end

    subgraph "Do API response (do_api_response)"
        history[(Message history\nSummary message\nSystem message)]
        saveMessage3[(Chatcmpl & Choice\nMessage)]
        api2[Get response w/ API]
    end

    subgraph "Do user response (do_user_response)"
        userInput[/User input/]
        saveMessage2[(Message)]
        stopQ{Stop?\nshould_stop}
        saveUser[Save user message]
    end

    subgraph "Summarize (summarize)"
        summarizeDB[(Message history)]
        summarizeQ{Summarize?\nshould_summarize}
        summarize[Summarize /w API]
        saveSummary[(Chatcmpl & Choice\nSummary message)]
    end
    stop([Stop])


    start([Start]) --> startStory
    initSys -.get_init_message.-> startStory

    startStory --> userInput
    userInput --> stopQ
    startStory -.save_api_response.-> saveMessage1

    api2 -.save_api_response.-> saveMessage3
    api2 --> summarizeQ

    stopQ -- Yes --> stop
    stopQ -- No --> saveUser
    saveUser -.save_user_response.-> saveMessage2

    saveUser --> api2
    history -.get_built_messages.-> api2

    summarize --> userInput
    summarizeQ -- No --> userInput
    summarizeQ -- Yes --> summarize
    summarizeDB -.get_summary_message_history.-> summarize
    summarize -.save_summary_message.-> saveSummary
```

## Entity Relationship Diagram

```mermaid
erDiagram
    User {
        Boolean is_whitelisted
    }

    Adventure {
        ManyToOne(User) user FK
        Text system_message
        Text start_message
        Text summary_message "Nullable"
        PositiveInteger iteration
    }

    Message {
        Datetime timestamp PK "Partial PK"
        ManyToOne(User) users FK,PK "Partial PK"
        Role role
        Text content
        Text name "Nullable"
    }

    Chatcmpl {
        Text id PK
        ManyToOne(User) users FK
        ManyToMany(Message) messages FK
        Text object_name
        Datetime created_at
        Text model
    }

    Choice {
        Foreign(Chatcmpl) chatcmpl FK,PK "Partial PK"
        PositiveInteger index PK "Partial PK"
        OneToOne(Message) message FK "Nullable"
        Text finish_reason
        PositiveInteger completion_tokens
        PositiveInteger prompt_tokens
    }

    User ||--o{ Adventure : plays

    Adventure ||--o{ Message : has

    Adventure ||--o{ Chatcmpl : calls

    Chatcmpl }|--o{ Message : takes

    Chatcmpl ||--|{ Choice : responds

    Message |o--o| Choice : chooses
```

## Environment Setup

### Python

We use Python 3.11, so make sure you have that installed.

You could use [pyenv](https://github.com/pyenv/pyenv) or [pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows is not recommended to install pyenv because it does not get native support) to manage your Python versions.

Install the Python version you want to use.
```bash
pyenv install 3.11
```

Specify the version for this directory.
```bash
pyenv local 3.11
```

To check your Python version, run `python --version` in your terminal.
```bash
python --version
```
Or you may need to specify the version explicitly if you didn't use pyenv or have multiple versions installed.
```bash
python3 --version
```

### Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

It is highly recommended to use the [venv](https://docs.python.org/3/library/venv.html) module that comes with Python.

To create a virtual environment in the `.venv` directory, run:
```bash
python -m venv .venv
```

Activate the environment.
```bash
# Linux, Bash, Mac OS X
source .venv/bin/activate
# Linux, Fish
source .venv/bin/activate.fish
# Linux, Csh
source .venv/bin/activate.csh
# Linux, PowerShell Core
.venv/bin/Activate.ps1
# Windows, cmd.exe
.venv\Scripts\activate.bat
# Windows, PowerShell
.venv\Scripts\Activate.ps1
```

Install the dependencies.
```bash
pip install -r requirements.txt
```

When you want to deactivate the virtual environment.
```bash
deactivate
```

### Lint and Pre-commit

We use [Flake8](https://flake8.pycqa.org) and [ISort](https://pycqa.github.io/isort/) for the coding style and guidelines. The style is then enforced by [pre-commit](https://pre-commit.com).

Finish the environment setup above (especially installing the dependencies with pip) before using pre-commit.

Install and setup pre-commit.
```bash
pre-commit install
```

To run pre-commit manually (only scans staged files).
```bash
pre-commit run --all-files
```

Remember to stage files again if there are any changes made by the pre-commit hooks or by you.
```bash
git add .
```

### VS Code Settings

You can add a workspace setting to automatically format your code on save using the black formatter.

You need to have the [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) VS Code extension installed.

Bring up the command palette with Ctrl+Shift+P(Windows/Linux) / Cmd+Shift+P(Mac) and search for "Preferences: Open Workspace Settings (JSON)".

Then replace the content with the following:
```json
{
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
    },
    "black-formatter.args": [
        "--line-length",
        "79",
        "--experimental-string-processing"
    ],
}
```

## Development

### Clone Repository

First clone the repository.
```bash
git clone git@github.com:LioQing/verbose-adventure.git
```

**Important**: You may need to setup SSH keys for your GitHub account. See [this guide](https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh) for more information.

### Checkout Branch

Then checkout the branch you want to work on.
```bash
git checkout <branch>
```

### Committing Changes

Commit your changes to the branch you are working on.
```bash
git add .
git commit -m "Your commit message"
```

Make any changes and stage your files again according to the pre-commit hooks.

### Pushing Changes

Set your branch's upstream branch to be the same branch on the remote repository on GitHub.
```bash
git push -u origin <branch>
```

After the first time you set the upstream branch, you can simply push without specifying the branch.
```bash
git push
```
