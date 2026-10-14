# Extension: greet by name

## What changes

The program can greet a person by name. Called with a name, it prints `hello <name>`; called without one, it still prints `hello world`.

## Flow

1. The person calls the program from the shell, with or without a name.
2. With a name, the program prints `hello <name>` to standard output; without one, `hello world`.
3. The program ends.

## What this touches in the original idea

The original idea kept input and parameters out of scope. This extension brings exactly one parameter, the name, into scope. A graphical interface and connections to other systems stay out of scope.
