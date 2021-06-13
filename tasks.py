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
        skipped = ("__init__.py", "main_window.py")
        if src.name in skipped or "register" in src.name or "dialog" in src.name:
            continue

        print(f"Generating QtDesigner plugin for {src.name}")
        content = src.read_text()
        match = re.search(r"class Ui_(.*?)\(", content)
        class_name = match.group(1)
        out = template.render(
            {"class_name": class_name, "module_name": src.with_suffix("").name}
        )
        src.with_name(f"register_{src.name}").write_text(out)

        class_definition = dedent(
            f"""

        class {class_name}(QWidget, Ui_{class_name}):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setupUi(self)
        """
        )
        src.write_text(content + class_definition)


@task(post=[generate_plugins, reformat_widgets_code])
def compile_ui(ctx):
    ui_dir = Path(__file__).parent / "ui"
    for ui_path in ui_dir.glob("*.ui"):
        out_path = (COMPILED_WIDGETS_DIR / ui_path.name).with_suffix(".py")
        ctx.run(f"pyside6-uic {ui_path} -o {out_path}", echo=True)


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
