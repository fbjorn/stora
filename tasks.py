import os
import re
from pathlib import Path
from shutil import rmtree
from textwrap import dedent

from invoke import task
from jinja2 import Template

ROOT = Path(__file__).parent
COMPILED_WIDGETS_DIR = ROOT / "app" / "widgets" / "auto"


@task
def stora(ctx):
    from app.main import main

    main()


@task
def reformat_widgets_code(ctx):
    ctx.run(f"black {COMPILED_WIDGETS_DIR}")


@task
def generate_plugins(ctx):
    template = Template((ROOT / "plugin.py.jinja2").read_text())

    for src in COMPILED_WIDGETS_DIR.glob("*.py"):
        if src.name.startswith(("register", "dialog", "_", "main_window")):
            continue

        print(f"Generating QtDesigner plugin for {src.name}")
        content = src.read_text()
        match = re.search(r"class Ui_(.*?)\(", content)
        class_name = match.group(1)
        out = template.render(
            {"class_name": class_name, "module_name": src.with_suffix("").name}
        )
        src.with_name(f"register_{src.name}").write_text(out)


@task(post=[generate_plugins, reformat_widgets_code])
def compile_ui(ctx):
    ui_dir = Path(__file__).parent / "ui"
    for ui_path in ui_dir.glob("*.ui"):
        py_path = (COMPILED_WIDGETS_DIR / ui_path.name).with_suffix(".py")
        ctx.run(f"pyside6-uic {ui_path} -o {py_path}", echo=True)

        # create custom classes so QtDesigner is able to import them later
        py_content = py_path.read_text()
        match = re.search(r"class Ui_(.*?)\(", py_content)
        class_name = match.group(1)
        patched = py_content.replace("from app.widgets.auto.", "from app.widgets.")
        if not py_path.name.startswith("dialog"):
            patched += dedent(
                f"""

                    class {class_name}(QWidget, Ui_{class_name}):
                        def __init__(self, *args, **kwargs):
                            super().__init__(*args, **kwargs)
                            self.setupUi(self)
                    """
            )
        py_path.write_text(patched)

        # Create new widget file if needed
        widget_file = ROOT / "app" / "widgets" / py_path.name
        if py_path.name.startswith("dialog"):
            widget_file = (
                ROOT
                / "app"
                / "widgets"
                / "dialogs"
                / py_path.name.removeprefix("dialog_")
            )
        if not widget_file.exists():
            print(f"Creating {widget_file}")
            name = py_path.with_suffix("").name
            content = dedent(
                f"""
            from app.widgets.auto.{name} import {class_name} as {class_name}Auto

            class {class_name}({class_name}Auto):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

            """
            )
            widget_file.write_text(content)


@task(post=[compile_ui])
def designer(ctx):
    for var in ("PYSIDE_DESIGNER_PLUGINS", "PYTHONPATH"):
        os.environ[var] = str(COMPILED_WIDGETS_DIR)
    ctx.run("pyside6-designer")


@task(pre=[compile_ui])
def pyinstaller(ctx):
    cmd = [
        "pyinstaller",
        "app/main.py",
        "-n Stora",
        "--windowed",
        '--osx-bundle-identifier "cc.fbjorn.stora"',
        "--icon assets/icon.png",
        "--clean",
    ]
    ctx.run(" ".join(cmd), echo=True)


@task(pre=[pyinstaller])
def build(ctx):
    dist = ROOT / "dist" / "Stora.app" / "Contents" / "MacOS"

    def copy_libs(package):
        src_dir = ROOT / ".venv" / "lib" / "python3.9" / "site-packages" / package
        for f in src_dir.glob("*"):
            out = dist / package / f.name
            if f.suffix not in (".dylib", ".so"):
                continue
            if f.suffix == ".so" and not out.exists():
                continue
            print(f)
            ctx.run(f"cp {f} {out}")

    # https://github.com/pyinstaller/pyinstaller/issues/5414#issuecomment-859347159
    print("Copying libraries")
    copy_libs("PySide6")
    copy_libs("shiboken6")

    print("Copying entire Qt folder")
    qt = ROOT / ".venv" / "lib" / "python3.9" / "site-packages" / "PySide6" / "Qt"
    qt_out = dist / "PySide6" / "Qt"
    ctx.run(f"cp -r {qt} {qt_out}")

    print("Cleanup Qt folder")
    rmtree(qt_out / "qml")
    rmtree(qt_out / "translations")
    useless_libs = (
        "Qt3D",
        "QtDesigner",
        "QtQuick",
        "QtShader",
        "QtVirt",
        "QtSql",
        "QtData",
        "QtCharts",
        "QtLabs",
        "QtScxml",
    )
    for d in (qt_out / "lib").glob("*"):
        if d.name.startswith(useless_libs):
            rmtree(d)

    plugins = ("platforms", "styles")
    for d in (qt_out / "plugins").glob("*"):
        if d.name not in plugins:
            rmtree(d)


@task
def release(ctx):
    toml = Path("pyproject.toml").read_text()
    match = re.search(r'version = "(.*?)"', toml)
    if match:
        version = match.group(1)
        print(f"Releasing {version}")
        ctx.run(f"git tag {version}", echo=True)
        ctx.run(f"git push origin {version}", echo=True)
    else:
        print("Failed to find version in the pyproject.toml")
