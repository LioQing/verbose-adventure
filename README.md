# Verbose Adventure

This is demo project for GPT interactive story generation.

## System Flow Diagram

### Scene

In Scene, NPC is an equivalent name for Adventure.

```mermaid
flowchart LR
    start((Start))
    stop((Stop))

    subgraph "Process User Selection (process_user_selection)"
        adventuresDB1[(NPCs)]
        selection[/Adventure selection/]
        exitQ{Exit?}
    end

    subgraph "Initialize Scene (init_scene)"
        construct[Constructor]
        adventuresDB[(NPCs)]
    end

    subgraph "Convo Coupler User Flow (ConvoCoupler.user_flow)"
        userflow[User flow]
        adventureDB[(ConvoCoupler)]
    end

    start --> construct
    construct -.create_npc.-> adventuresDB

    userflow --> selection
    adventureDB -.get_npc_user_flow.-> userflow

    construct --> selection
    adventuresDB1 -.get_npcs.-> selection
    selection --> exitQ
    exitQ -- Yes --> stop
    exitQ -- No --> userflow
```

### Adventure

```mermaid
flowchart LR
    subgraph "Initialize story (init_story)"
        startStory[Start story w/ API]
        initSys[(System message\nStart message)]
        saveMessage1[(Chatcmpl & Choice\nMessage)]
    end

    subgraph "Process API response (process_api_response)"
        history[(Message history\nSummary message\nSystem message)]
        saveMessage3[(Chatcmpl & Choice\nMessage)]
        api2[Get response w/ API]
    end

    subgraph "Process user response (process_user_response)"
        userInput[/User input/]
        saveMessage2[(Message)]
        stopQ{Stop?\nshould_stop}
        saveUser[Save user message]
    end

    subgraph "Summarize (summarize)"
        summarizeDB[(Message history\nSummary message)]
        summarizeQ{Summarize?\nshould_summarize}
        summarize[Summarize /w API]
        saveSummary[(Chatcmpl & Choice\nSummary message)]
    end
    stop([Stop])
    start([Start])
    output1[/Output API/]
    output2[/Output API/]

    start --> startStory
    initSys -.get_init_message.-> startStory
    output1 --> userInput

    startStory -.save_api_response.-> saveMessage1
    startStory --> output1
    userInput --> stopQ

    output2 --> summarizeQ
    api2 -.save_api_response.-> saveMessage3
    api2 --> output2

    stopQ -- No --> saveUser
    stopQ -- Yes --> stop

    saveUser --> api2
    history -.get_built_messages.-> api2
    saveUser -.save_user_response.-> saveMessage2

    summarize --> userInput
    summarizeQ -- No --> userInput
    summarizeQ -- Yes --> summarize
    summarizeDB -.get_summary_messages.-> summarize
    summarize -.save_summary_response.-> saveSummary
```

## Entity Relationship Diagram

```mermaid
erDiagram
    User {
        Boolean is_whitelisted
    }

    Summary {
        Text summary
    }

    SceneRunner {
        ManyToOne(User) user FK
        ManyToOne(Scene) scene FK
    }

    Scene {
        Text id PK
        Text name
        Text system_message
    }

    SceneNpcAdventurePair {
        ManyToOne(SceneRunner) runner FK
        ManyToOne(SceneNpc) npc FK
        OneToOne(Adventure) adventure FK
        PositiveInteger knowledge_selection_token_count
    }

    SceneNpc {
        Text id PK
        Text name
        Text title
        Text character
        ManyToOne(Scene) scene FK
        ManyToMany(SceneNpc) knowledges FK
    }

    Knowledge {
        Text id PK
        Text name
        Text description
        Text knowledge
    }

    Adventure {
        ManyToOne(User) user FK
        OneToOne(Summary) summary FK "Nullable"
        OneToOne(Message) latest_message FK "Nullable"
        Text system_message
        Text start_message
        PositiveInteger iteration
    }

    Chatcmpl {
        Text id PK
        ManyToOne(Adventure) adventure FK
        ManyToOne(Summary) summary FK "Nullable"
        ManyToMany(Message) messages FK
        ChatcmplKind kind "Message, Summary"
        Text object_name
        Datetime created_at
        Text model
        PositiveInteger completion_tokens
        PositiveInteger prompt_tokens
    }

    Message {
        Datetime timestamp PK "Partial PK"
        ManyToOne(Adventure) adventure FK,PK "Partial PK"
        OneToOne(Message) prev FK "Nullable"
        Role role "System, Assistant, User, Function"
        Text content
        Text name "Nullable"
    }

    Choice {
        ManyToOne(Chatcmpl) chatcmpl FK,PK "Partial PK"
        PositiveInteger index PK "Partial PK"
        OneToOne(Message) message FK "Nullable"
        OneToOne(Summary) summary FK "Nullable"
        Text finish_reason
    }

    User ||--o{ SceneRunner : runs

    User ||--o{ Adventure : plays

    SceneRunner }|--|| Scene : runs

    SceneRunner ||--|{ SceneNpcAdventurePair : has

    Scene ||--|{ SceneNpc : npcs

    SceneNpcAdventurePair }|--|| SceneNpc : npc

    SceneNpcAdventurePair ||--|| Adventure : adventure

    SceneNpc }|--|{ Knowledge : knows

    Message }o--o{ Message : prev

    Adventure ||--o| Message : has

    Adventure ||--o{ Chatcmpl : calls

    Chatcmpl }|--o{ Message : takes

    Chatcmpl ||--|{ Choice : responds

    Summary |o--o| Adventure : current

    Summary |o--o{ Chatcmpl : takes

    Summary ||--o| Choice : chooses

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

### Environment Variables

Make a copy of the `.env.example` file and rename it to `.env`.
```bash
cp .env.example .env
```

Fill in the environment variables in the `.env` file.

## Running the Project

There are 3 ways to run the project, using Docker, using the database + Django locally, or using the standalone program.

The production environment is deployed using Docker. However, you can also use the database + Django locally for development because it is the same build as the production environment.

The standalone program is used for quickly testing the engine without the database and Django during development.

### Standalone Program

Simply run the `standalone/main.py` file as a Python module.
```bash
python -m standalone.main
```

### Docker

You can skip the database and Django setup if you use [Docker](https://www.docker.com).

You have to make sure the environment variables in the `.env` file are set correctly, the port is set to 5433 in `docker-compose.yml` file to avoid conflict with the local database.
```bash
# Windows
DB_HOST = host.docker.internal
DB_PORT = 5433
# Linux, Mac OS X
DB_HOST = 127.17.0.1    # or any IP address you set explicitly
DB_PORT = 5433
```

Make sure you have Docker installed.
```bash
docker --version
```

Also make sure you have [Docker Compose](https://docs.docker.com/compose) installed.
```bash
docker-compose --version
```

Run and build the images.
```bash
docker-compose up
```

Despite `verbose-adventure-web-1` says server is at http://0.0.0.0:8000/, you should use http://localhost:8001/ defined in the `docker-compose.yml` file.

When you want to stop the containers.
```bash
docker-compose down
```

### Database + Django

Use [PostgreSQL](https://www.postgresql.org) as the database.

You have to make sure the environment variables in the `.env` file are set correctly.
```bash
DB_HOST = localhost
DB_PORT = 5432          # default postgresql port
```

Run the Django migrations.
```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser.
```bash
python manage.py createsuperuser
```

Run the server.
```bash
python manage.py runserver
```

## Code Style Enforcement

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
