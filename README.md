# Proc Compose

Monitor several processes at once.

## Running

Right now the config is stored in the `tool` section of `pyproject.toml`:

```toml
[tool.proc-compose]
colorize = false

[tool.proc-compose.commands]
build-frontend = "npm run build:watch"
webserver = "pserve --reload development.ini"

```

And then run `proc-compose`:

```
build-frontend |
build-frontend | > build
build-frontend | > esbuild --watch test.js --outfile=test.out.js
build-frontend |
build-frontend | [watch] build finished, watching for changes...
webserver      | Starting monitor for PID 4054312.
webserver      | Starting server in PID 4054312.
```
