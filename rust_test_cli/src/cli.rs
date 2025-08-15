//! CLI command definitions and parsing logic



use clap::Command;



pub fn build_cli() -> Command {

    Command::new(env!("CARGO_PKG_NAME"))

        .about(env!("CARGO_PKG_DESCRIPTION"))

        .version(env!("CARGO_PKG_VERSION"))

}

