import typer # type: ignore

app = typer.Typer()

@app.command()
def greet(name: str):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")

@app.command()
def add(x: int, y: int):
    """Add two numbers."""
    typer.echo(f"The result is: {x + y}")

if __name__ == "__main__":
    app()
