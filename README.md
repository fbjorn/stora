# Stora - Firestore GUI Client

## Motivation

We use Google's Firestore as a main database on our work. It provides
some emulator to run DB locally. Unfortunately, I failed to find
a convenient GUI tool for browsing data in Firestore. They're either
don't support emulator at all, or inconvenient, or paid.

So I decided to reinvent the wheel.

## Development

```shell
pre-commit install
poetry install

poetry run invoke compile-ui
poetry run invoke stora
```

Please use QtDesigner for layout modifications.

```shell
poetry run invoke designer
```
