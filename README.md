Exactly. That explains your `Finished: SUCCESS`: Jenkins successfully fetched an **empty Jenkinsfile**, so there was nothing to execute.

Let's fix it now.

## 1. Open `Jenkinsfile` in VS Code

Your local project:

```text
jenkins-python-demo/
├── app/
├── tests/
├── requirements.txt
├── Jenkinsfile      ← open this
└── build.py
```

Put this complete pipeline into `Jenkinsfile`:

```groovy
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'

                bat '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running Flake8...'

                bat '''
                    flake8 app tests
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'

                bat '''
                    pytest -v
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'

                bat '''
                    python build.py
                '''
            }
        }
    }

    post {

        success {
            echo '================================'
            echo 'PIPELINE SUCCESSFUL'
            echo '================================'
        }

        failure {
            echo '================================'
            echo 'PIPELINE FAILED'
            echo '================================'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}
```

Save the file.

---

# 2. Check the file locally

From your project directory:

```powershell
Get-Content .\Jenkinsfile
```

You should see the Groovy pipeline you just added.

---

# 3. Commit the Jenkinsfile

This is important.

Jenkins is reading the file from **GitHub**, not your local VS Code folder.

Run:

```powershell
git status
```

You should see:

```text
modified: Jenkinsfile
```

Then:

```powershell
git add Jenkinsfile
```

```powershell
git commit -m "Add Jenkins CI pipeline"
```

Then push it:

```powershell
git push
```

---

# 4. Verify GitHub

Go back to your repository and click:

**Jenkinsfile**

You should now see the pipeline code.

This step matters because Jenkins will read:

```text
GitHub
   ↓
jenkins-python-demo
   ↓
Jenkinsfile
```

not:

```text
Your VS Code
   ↓
Jenkins
```

---

# 5. Run Jenkins again

Go to:

```text
Jenkins
  ↓
jenkins-python-demo
  ↓
Build Now
```

This should create:

```text
Build #3
```

Then click:

```text
#3
  ↓
Console Output
```

---

# 6. What should happen

This time you should see actual stages:

```text
[Pipeline] Start of Pipeline

[Pipeline] stage
[Pipeline] { (Checkout)
Checking out source code...

[Pipeline] stage
[Pipeline] { (Install Dependencies)
Installing Python dependencies...

[Pipeline] stage
[Pipeline] { (Code Quality)
Running Flake8...

[Pipeline] stage
[Pipeline] { (Run Tests)
Running unit tests...

5 passed

[Pipeline] stage
[Pipeline] { (Build)
Building application...

Starting application build...
Application copied to build directory.
Build completed successfully.

PIPELINE SUCCESSFUL

[Pipeline] End of Pipeline

Finished: SUCCESS
```

---

## One thing I expect might fail

Your Jenkins service has its own environment.

Your local terminal has:

```text
(venv)
```

and therefore:

```text
pytest
flake8
python
```

are available.

Jenkins may not have `pytest` and `flake8` available initially.

However, our Jenkinsfile does:

```groovy
bat '''
    python -m pip install --upgrade pip
    pip install -r requirements.txt
'''
```

so it installs `pytest` and `flake8` before using them.

The bigger question is whether Jenkins can find:

```text
python
```

If you get:

```text
'python' is not recognized as an internal or external command
```

that's the next thing we'll fix.

---

# Your pipeline now has a real purpose

After this change:

```text
             GitHub
                │
                │ Jenkins reads Jenkinsfile
                ▼
             Jenkins
                │
                ▼
          ┌─────────────┐
          │   Checkout  │
          └──────┬──────┘
                 ▼
       ┌──────────────────┐
       │ Install packages │
       └────────┬─────────┘
                ▼
       ┌──────────────────┐
       │     Flake8       │
       └────────┬─────────┘
                ▼
       ┌──────────────────┐
       │      Pytest      │
       └────────┬─────────┘
                ▼
       ┌──────────────────┐
       │      Build       │
       └────────┬─────────┘
                ▼
             SUCCESS
```

### Do these now:

```powershell
git add Jenkinsfile
git commit -m "Add Jenkins CI pipeline"
git push
```

Then **Build Now → Console Output**.

If it fails, paste the Console Output here. The failure will tell us exactly which Jenkins stage needs configuration.


Good — the console output gives us the exact problem. **Jenkins itself is working correctly. GitHub checkout is working correctly. The failure is only Python.**

The key lines are:

```text
'python' is not recognized as an internal or external command
'pip' is not recognized as an internal or external command
```

### Why this happens

Your normal PowerShell has Python because your user environment/virtual environment knows where Python is.

But Jenkins is running as a **Windows service**, with a different environment:

```text
Your PowerShell
    ↓
Python available ✅

Jenkins Windows Service
    ↓
Python not available ❌
```

Also, this line:

```text
Selected Git installation does not exist. Using Default
```

is **not the problem**. Jenkins successfully found Git:

```text
git version 2.55.0.windows.5
```

So leave Git alone for now.

---

# Step 1 — Find your real Python installation

Open a **normal PowerShell** (not Jenkins Script Console) and run:

```powershell
where.exe python
```

Also run:

```powershell
python -c "import sys; print(sys.executable)"
```

You will probably get something like:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312\python.exe
```

We need the **actual Python installation**, not:

```text
...\jenkins-python-demo\venv\Scripts\python.exe
```

because Jenkins should create/use its own build environment rather than your personal VS Code virtual environment.

---

# Step 2 — Add Python to Windows System PATH

Suppose your output is:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312\python.exe
```

Then the Python directory is:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312
```

and Scripts is:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312\Scripts
```

We need both available to Jenkins.

### Open:

```text
Windows Search
    ↓
Environment Variables
    ↓
Edit the system environment variables
    ↓
Environment Variables
```

Under **System variables**, find:

```text
Path
```

Click:

**Edit → New**

Add:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312
```

Then add:

```text
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312\Scripts
```

⚠️ Use **your actual paths** from `where.exe python`, not necessarily the example above.

---

# Step 3 — Restart Jenkins

This step is critical.

Jenkins is already running as a Windows service. It won't automatically pick up the newly changed PATH.

Open PowerShell **as Administrator**:

```powershell
Restart-Service Jenkins
```

Then check:

```powershell
Get-Service Jenkins
```

You want:

```text
Status
------
Running
```

---

# Step 4 — Verify from Jenkins

Go to:

```text
Jenkins
→ Manage Jenkins
→ Script Console
```

Or:

```text
http://localhost:8080/script
```

Run:

```groovy
def process = "python --version".execute()
process.waitFor()

println "Exit code: " + process.exitValue()
println "Output: " + process.text
println "Error: " + process.err.text
```

You want:

```text
Exit code: 0
Output: Python 3.12.10
```

If that happens, Jenkins can now find Python.

---

# Step 5 — Check pip too

Run:

```groovy
def process = "python -m pip --version".execute()
process.waitFor()

println "Exit code: " + process.exitValue()
println process.text
println process.err.text
```

Expected something like:

```text
pip 25.x from ...
```

---

# Step 6 — Run Jenkins again

Go back to:

```text
jenkins-python-demo
```

Click:

**Build Now**

You should now get:

```text
Checkout                  ✅
Install Dependencies      ✅
Code Quality              ...
Run Tests                 ...
Build                     ...
```

The Install stage should execute:

```text
python -m pip install --upgrade pip
pip install -r requirements.txt
```

and install:

```text
pytest
flake8
```

Then:

```text
Code Quality
    ↓
flake8 app tests

Run Tests
    ↓
pytest -v

Build
    ↓
python build.py
```

---

# One improvement I recommend

Change this:

```groovy
pip install -r requirements.txt
```

to:

```groovy
python -m pip install -r requirements.txt
```

Using `python -m pip` is more reliable because it guarantees you're using pip associated with the Python interpreter Jenkins found.

So your stage should be:

```groovy
stage('Install Dependencies') {
    steps {
        echo 'Installing Python dependencies...'

        bat '''
            python -m pip install --upgrade pip
            python -m pip install -r requirements.txt
        '''
    }
}
```

---

## Your Jenkins pipeline is actually progressing correctly

Look carefully at your current output:

```text
GitHub checkout       ✅
Jenkinsfile           ✅
Jenkins pipeline      ✅
Install Dependencies  ❌
Code Quality          ⏭️
Run Tests             ⏭️
Build                 ⏭️
```

So we **do not need to change GitHub, Git, Jenkins, or your Python code**.

We only need to expose Python to the Jenkins Windows service.

### Do this first

Run in your normal PowerShell:

```powershell
where.exe python
```

```powershell
python -c "import sys; print(sys.executable)"
```

**Send me those two outputs.** I'll give you the exact two PATH entries for your machine, rather than making you guess the Python installation location.


Good — we have found the **next exact issue**. Your Python setup is now working. ✅

The failure is here:

```text
Successfully installed flake8 ...
```

followed by:

```text
'flake8' is not recognized as an internal or external command
```

And Jenkins explicitly tells us why:

```text
The script flake8.exe is installed in
C:\Users\Rahul chaudhry\AppData\Local\Programs\Python\Python312\Scripts
which is not on PATH.
```

### The important point

Python can find the packages:

```text
python -m pip install ...
        ↓
pytest / flake8 installed
```

But Windows cannot directly find:

```text
flake8.exe
pytest.exe
```

because the `Scripts` directory isn't available on Jenkins' PATH.

We **don't need to modify Windows PATH again**. A better solution for this Jenkins pipeline is to invoke the tools through Python.

---

# Step 1 — Change your Jenkinsfile

Open your local `Jenkinsfile`.

Change:

```groovy
stage('Code Quality') {
    steps {
        echo 'Running Flake8...'

        bat '''
            flake8 app tests
        '''
    }
}
```

to:

```groovy
stage('Code Quality') {
    steps {
        echo 'Running Flake8...'

        bat '''
            python -m flake8 app tests
        '''
    }
}
```

And change your test stage from:

```groovy
stage('Run Tests') {
    steps {
        echo 'Running unit tests...'

        bat '''
            pytest -v
        '''
    }
}
```

to:

```groovy
stage('Run Tests') {
    steps {
        echo 'Running unit tests...'

        bat '''
            python -m pytest -v
        '''
    }
}
```

---

# Your complete Jenkinsfile

I recommend making it exactly this:

```groovy
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'

                bat '''
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running Flake8...'

                bat '''
                    python -m flake8 app tests
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'

                bat '''
                    python -m pytest -v
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'

                bat '''
                    python build.py
                '''
            }
        }
    }

    post {

        success {
            echo '================================'
            echo 'PIPELINE SUCCESSFUL'
            echo '================================'
        }

        failure {
            echo '================================'
            echo 'PIPELINE FAILED'
            echo '================================'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}
```

---

# Why `python -m` fixes it

This is an important Python concept.

### Your current approach

```text
flake8 app tests
```

Windows searches PATH for:

```text
flake8.exe
```

But Jenkins doesn't have:

```text
Python312\Scripts
```

on PATH.

Therefore:

```text
flake8.exe
    ↓
PATH search
    ↓
NOT FOUND ❌
```

---

### New approach

```text
python -m flake8 app tests
```

We're telling Python:

> Find the installed `flake8` module and execute it using this Python interpreter.

So:

```text
python
  ↓
Python 3.12
  ↓
find flake8 module
  ↓
execute flake8
  ↓
SUCCESS
```

Same thing for pytest:

```text
python -m pytest -v
```

This is generally a more reliable way to run Python CLI tools in CI.

---

# Step 2 — Test it locally first

Before pushing to GitHub, you can test exactly the commands Jenkins will use.

From your project directory:

```powershell
python -m flake8 app tests
```

You should get **no output** and return to the prompt.

Then:

```powershell
python -m pytest -v
```

You should get:

```text
5 passed
```

Then:

```powershell
python build.py
```

Expected:

```text
Starting application build...
Application copied to build directory.
Build completed successfully.
```

---

# Step 3 — Push the change

```powershell
git add Jenkinsfile
```

```powershell
git commit -m "Run Python tools through module execution"
```

```powershell
git push
```

---

# Step 4 — Build Jenkins again

Go to:

```text
Jenkins
   ↓
jenkins-python-demo
   ↓
Build Now
```

This will be your **Build #5**.

The pipeline should now progress:

```text
Declarative: Checkout SCM     ✅
       ↓
Checkout                       ✅
       ↓
Install Dependencies           ✅
       ↓
Code Quality                   ✅
       ↓
Run Tests                      ✅
       ↓
Build                          ✅
       ↓
SUCCESS                        🟢
```

And in the test stage:

```text
5 passed
```

---

## Also, ignore this warning for now

You saw:

```text
WARNING: The script flake8.exe is installed in ...
Scripts which is not on PATH.
```

That's **not an installation failure**.

The package installation succeeded:

```text
Successfully installed ... flake8 ... pytest ...
```

The warning only means:

> You cannot type `flake8` directly from this environment because its executable directory isn't on PATH.

Our new commands:

```bash
python -m flake8
python -m pytest
```

solve exactly that problem.

---

### One more observation

You currently have:

```text
Declarative: Checkout SCM
        +
Checkout
```

So your repository is being checked out **twice**. It isn't causing this failure, but it's unnecessary.

Once Build #5 is green, I'd clean that up so the pipeline is:

```text
Checkout
   ↓
Install Dependencies
   ↓
Code Quality
   ↓
Run Tests
   ↓
Build
```

Then the next useful step is **GitHub webhook → Jenkins automatic trigger**, so a `git push` automatically starts the pipeline instead of you manually clicking **Build Now**.
Good. **Flake8 and pytest are completely fine now.** ✅

The only remaining problem is your `build.py`:

```text
PermissionError: [WinError 5] Access is denied:
'build\app\__pycache__'
```

This is a **Windows file-lock/permission issue**, not a Python testing issue.

Your current sequence is:

```text
flake8        ✅
pytest        ✅ 5 passed
build.py      ❌ cannot delete old build directory
```

## 1. First, delete the old `build` directory manually

From your project directory, run:

```powershell
Remove-Item -Recurse -Force .\build
```

If it succeeds, run:

```powershell
python build.py
```

You should get:

```text
Starting application build...
Application copied to build directory.
Build completed successfully.
```

---

## 2. If `Remove-Item` also gives Access Denied

Because your project is inside:

```text
OneDrive\VSCode\learning projects\
```

OneDrive can sometimes temporarily lock files.

First close:

* VS Code
* File Explorer windows opened inside the `build` directory
* Any Python process running from this project

Then try:

```powershell
Remove-Item -Recurse -Force .\build
```

If it still fails, restart Windows and try the same command.

---

# 3. But I recommend fixing `build.py`

Your current `build.py` probably contains something similar to:

```python
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
```

That's fragile on Windows.

Let's make the build script more robust.

Replace your `build.py` with:

```python
import os
import shutil


BUILD_DIR = "build"
SOURCE_DIR = "app"


def build_application():
    print("Starting application build...")

    # Remove previous build
    if os.path.exists(BUILD_DIR):
        print("Removing previous build...")
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # Create build directory
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Copy application
    shutil.copytree(
        SOURCE_DIR,
        os.path.join(BUILD_DIR, SOURCE_DIR)
    )

    print("Application copied to build directory.")
    print("Build completed successfully.")


if __name__ == "__main__":
    build_application()
```

However, there's an important caveat: `ignore_errors=True` can hide a failure to remove the old directory. **For a CI pipeline, silently ignoring build cleanup errors isn't ideal.**

A better version for learning Jenkins is:

```python
import os
import shutil


BUILD_DIR = "build"
SOURCE_DIR = "app"


def build_application():
    print("Starting application build...")

    # Remove previous build
    if os.path.exists(BUILD_DIR):
        print("Removing previous build...")
        shutil.rmtree(BUILD_DIR)

    # Create build directory
    os.makedirs(BUILD_DIR)

    # Copy application
    shutil.copytree(
        SOURCE_DIR,
        os.path.join(BUILD_DIR, SOURCE_DIR)
    )

    print("Application copied to build directory.")
    print("Build completed successfully.")


if __name__ == "__main__":
    build_application()
```

That's actually better for your Jenkins demonstration because **if cleanup fails, Jenkins should know the build failed rather than pretending it succeeded.**

---

# 4. Important: don't put `__pycache__` into your build

There is another improvement I'd make.

Your error is specifically:

```text
build\app\__pycache__
```

You don't really want Python cache files in your application build artifact.

Change:

```python
shutil.copytree(
    SOURCE_DIR,
    os.path.join(BUILD_DIR, SOURCE_DIR)
)
```

to:

```python
shutil.copytree(
    SOURCE_DIR,
    os.path.join(BUILD_DIR, SOURCE_DIR),
    ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
)
```

So your final `build.py` becomes:

```python
import os
import shutil


BUILD_DIR = "build"
SOURCE_DIR = "app"


def build_application():
    print("Starting application build...")

    # Remove previous build
    if os.path.exists(BUILD_DIR):
        print("Removing previous build...")
        shutil.rmtree(BUILD_DIR)

    # Create build directory
    os.makedirs(BUILD_DIR)

    # Copy application without Python cache files
    shutil.copytree(
        SOURCE_DIR,
        os.path.join(BUILD_DIR, SOURCE_DIR),
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc"
        )
    )

    print("Application copied to build directory.")
    print("Build completed successfully.")


if __name__ == "__main__":
    build_application()
```

---

# 5. Test locally

First:

```powershell
Remove-Item -Recurse -Force .\build
```

Then:

```powershell
python build.py
```

Expected:

```text
Starting application build...
Application copied to build directory.
Build completed successfully.
```

Check the result:

```powershell
Get-ChildItem .\build -Recurse
```

You should have something like:

```text
build
└── app
    ├── __init__.py
    └── calculator.py
```

Notice there should **not** be:

```text
__pycache__
```

---

# 6. Then push to GitHub

```powershell
git add build.py
git commit -m "Improve Python application build"
git push
```

Then in Jenkins:

```text
jenkins-python-demo
        ↓
Build Now
```

---

## Your Jenkins pipeline is now very close

You've already demonstrated:

```text
GitHub
   │
   ▼
Jenkins
   │
   ├── Checkout              ✅
   │
   ├── Install Python deps  ✅
   │
   ├── Flake8               ✅
   │
   ├── Pytest               ✅
   │      └── 5 passed
   │
   └── Build                ⏳
```

So **don't change the Jenkins/Python configuration anymore**. The current failure is isolated to `build.py` and the Windows `build` directory.

### Do this first:

```powershell
Remove-Item -Recurse -Force .\build
python build.py
```

If that works, update `build.py` with the improved version above, push it, and run the Jenkins build again.
