import subprocess
import argparse
from pathlib import Path

env = {
    "SUPPRESS_POSSUM": "true",
    "RUN_LOCAL": "true",
    "USE_FIND_ALGORITHM": "true",
    "LOG_LEVEL": "VERBOSE",
}

validators = {
    "VALIDATE_ANSIBLE",
    "VALIDATE_ARM",
    "VALIDATE_BASH",
    "VALIDATE_BASH_EXEC",
    "VALIDATE_CPP",
    "VALIDATE_CLANG_FORMAT",
    "VALIDATE_CLOJURE",
    "VALIDATE_CLOUDFORMATION",
    "VALIDATE_COFFEESCRIPT",
    "VALIDATE_CSHARP",
    "VALIDATE_CSS",
    "VALIDATE_DART",
    "VALIDATE_DOCKERFILE_HADOLINT",
    "VALIDATE_EDITORCONFIG",
    "VALIDATE_ENV",
    "VALIDATE_GHERKIN",
    "VALIDATE_GITHUB_ACTIONS",
    "VALIDATE_GITLEAKS",
    "VALIDATE_GO",
    "VALIDATE_GOOGLE_JAVA_FORMAT",
    "VALIDATE_GROOVY",
    "VALIDATE_HTML",
    "VALIDATE_JAVA",
    "VALIDATE_JAVASCRIPT_ES",
    "VALIDATE_JAVASCRIPT_STANDARD",
    "VALIDATE_JSCPD",
    "VALIDATE_JSON",
    "VALIDATE_JSX",
    "VALIDATE_KOTLIN",
    "VALIDATE_KOTLIN_ANDROID",
    "VALIDATE_KUBERNETES_KUBECONFORM",
    "VALIDATE_LATEX",
    "VALIDATE_LUA",
    "VALIDATE_MARKDOWN",
    "VALIDATE_NATURAL_LANGUAGE",
    "VALIDATE_OPENAPI",
    "VALIDATE_PERL",
    "VALIDATE_PHP",
    "VALIDATE_PHP_BUILTIN",
    "VALIDATE_PHP_PHPCS",
    "VALIDATE_PHP_PHPSTAN",
    "VALIDATE_PHP_PSALM",
    "VALIDATE_POWERSHELL",
    "VALIDATE_PROTOBUF",
    "VALIDATE_PYTHON",
    "VALIDATE_PYTHON_BLACK",
    "VALIDATE_PYTHON_FLAKE8",
    "VALIDATE_PYTHON_ISORT",
    "VALIDATE_PYTHON_MYPY",
    "VALIDATE_PYTHON_PYLINT",
    "VALIDATE_R",
    "VALIDATE_RAKU",
    "VALIDATE_RUBY",
    "VALIDATE_RUST_2015",
    "VALIDATE_RUST_2018",
    "VALIDATE_RUST_2021",
    "VALIDATE_RUST_CLIPPY",
    "VALIDATE_SCALAFMT",
    "VALIDATE_SHELL_SHFMT",
    "VALIDATE_SNAKEMAKE_LINT",
    "VALIDATE_SNAKEMAKE_SNAKEFMT",
    "VALIDATE_STATES",
    "VALIDATE_SQL",
    "VALIDATE_SQLFLUFF",
    "VALIDATE_TEKTON",
    "VALIDATE_TERRAFORM_FMT",
    "VALIDATE_TERRAFORM_TERRASCAN",
    "VALIDATE_TERRAFORM_TFLINT",
    "VALIDATE_TERRAGRUNT",
    "VALIDATE_TSX",
    "VALIDATE_TYPESCRIPT_ES",
    "VALIDATE_TYPESCRIPT_STANDARD",
    "VALIDATE_XML",
    "VALIDATE_YAML",
}

# To fix
# BASH:[14]
# DOCKERFILE_HADOLINT:[2]
# PYTHON_PYLINT:[4]
# PYTHON_FLAKE8:[17]
# PYTHON_ISORT:[25]
# PYTHON_MYPY:[13]
# TERRAFORM_TFLINT:[8]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".")
    parser.add_argument("--image", default="github/super-linter:latest")
    parser.add_argument("-l", "--lint", default="")
    args = parser.parse_args()
    volume = Path(args.dir).resolve()
    cmd = ["docker", "run", "-v", f"{volume}:/tmp/lint"]

    linters = [x.strip() for x in args.lint.split(",") if x.strip() != ""]

    for key, value in env.items():
        cmd.append("-e")
        cmd.append(f"{key}={value}")

    for validator in validators:
        if not any(linter.lower() in validator.lower() for linter in linters):
            cmd.append("-e")
            cmd.append(f"{validator}=false")

    cmd.append(args.image)
    p = subprocess.run(cmd)
    exit(p.returncode)
