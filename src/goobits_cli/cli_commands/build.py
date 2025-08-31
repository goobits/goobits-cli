"""Build command implementation for goobits CLI.

This module contains the build command that generates CLI applications and
setup scripts from goobits.yaml configuration files. It handles multi-language
generation, file operations, and logging.
"""

import uuid
from pathlib import Path
from typing import Optional

import typer


def build_command(
    config_path: Optional[Path] = typer.Argument(
        None, help="Path to goobits.yaml file (defaults to ./goobits.yaml)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (defaults to same directory as config file)",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output filename for generated CLI (defaults to 'generated_cli.py')",
    ),
    backup: bool = typer.Option(
        False,
        "--backup",
        help="Create backup files (.bak) when overwriting existing files",
    ),
):
    """
    Build CLI and setup scripts from goobits.yaml configuration.

    This command reads a goobits.yaml file and generates:

    - CLI script: Generated from goobits.yaml (default: generated_cli.py)

    - setup.sh: Project setup script

    Use --output to specify a custom CLI filename (e.g., --output cli.py)
    """
    # Import required utilities (avoiding circular imports)
    from ..main import (
        _lazy_imports,
        load_goobits_config,
        backup_file,
        extract_version_from_pyproject,
    )
    from ..logger import set_context, get_logger, clear_context
    
    _lazy_imports()

    # Set up logging context for build operation
    operation_id = str(uuid.uuid4())[:8]
    set_context(operation="build", operation_id=operation_id)

    logger = get_logger(__name__)
    logger.info("Starting build operation")

    # Determine config file path
    if config_path is None:
        config_path = Path.cwd() / "goobits.yaml"

    config_path = Path(config_path).resolve()

    # Add config context
    set_context(config_file=str(config_path))

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        typer.echo(f"Error: Configuration file '{config_path}' not found.", err=True)
        raise typer.Exit(1)

    # Determine output directory
    if output_dir is None:
        output_dir = config_path.parent
    else:
        output_dir = Path(output_dir).resolve()

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Loading configuration from: {config_path}")

    # Show backup status
    if not backup:
        typer.echo("💡 Backups disabled (use --backup to create .bak files)")
        typer.echo("💡 Ensure your changes are committed to git before proceeding")

    # Universal Template System is always enabled
    typer.echo("⚡ Using Universal Template System with single-file output")

    # Load goobits configuration
    logger.info("Loading goobits configuration")
    goobits_config = load_goobits_config(config_path)

    # Detect target languages from configuration
    target_languages = goobits_config.get_target_languages()

    # Add package name to context
    set_context(package_name=goobits_config.package_name)

    if len(target_languages) == 1:
        logger.info(f"Detected language: {target_languages[0]}")
        typer.echo(f"Detected language: {target_languages[0]}")
    else:
        logger.info(f"Detected multi-language targets: {', '.join(target_languages)}")
        typer.echo(f"Detected multi-language targets: {', '.join(target_languages)}")

    # Universal Template System is now the default
    typer.echo("✅ Using Universal Template System (production-ready)")
    typer.echo("   Generating optimized cross-language CLI with enhanced features.")

    typer.echo("Generating CLI scripts...")

    # Generate CLI for each target language
    if goobits_config.cli:
        # Extract version from pyproject.toml if available
        pyproject_path = output_dir / "pyproject.toml"
        version = None

        if pyproject_path.exists():
            version = extract_version_from_pyproject(output_dir)

        # Multi-language generation loop
        for language in target_languages:
            # Add current language to context
            set_context(language=language)
            
            if len(target_languages) > 1:
                typer.echo(f"🚀 Generating {language} CLI using Universal Template System")
            
            # Route to appropriate generator based on language
            if language == "nodejs":
                from goobits_cli.generators.nodejs import NodeJSGenerator
                generator = NodeJSGenerator()
            elif language == "typescript":
                from goobits_cli.generators.typescript import TypeScriptGenerator
                generator = TypeScriptGenerator()
            elif language == "rust":
                from goobits_cli.generators.rust import RustGenerator
                generator = RustGenerator()
            else:  # python (default)
                from goobits_cli.generators.python import PythonGenerator
                generator = PythonGenerator()

            # Generate all files for this language
            all_files = generator.generate_all_files(
                goobits_config, config_path.name, version
            )

            # Determine output directory for this language
            if len(target_languages) > 1:
                # Multi-language: organize by language subdirectories
                lang_output_dir = output_dir / language
                lang_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                # Single language: use the main output directory
                lang_output_dir = output_dir

            # Write all generated files for this language
            executable_files = all_files.pop("__executable__", [])

            for file_path, content in all_files.items():
                # Skip pyproject.toml when building goobits itself (self-hosting)
                if (
                    file_path == "pyproject.toml"
                    and goobits_config.package_name == "goobits-cli"
                ):
                    typer.echo(
                        "⏭️  Skipping pyproject.toml for self-hosted goobits-cli"
                    )
                    continue

                full_path = lang_output_dir / file_path

                # Ensure parent directories exist
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Backup existing file if requested
                backup_path = backup_file(full_path, backup)
                if backup_path:
                    typer.echo(f"📋 Backed up existing file: {backup_path}")

                # Write the file
                try:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    logger.info(f"Generated file: {full_path}")
                    typer.echo(f"📝 Generated: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to write {full_path}: {e}")
                    typer.echo(f"❌ Error writing {file_path}: {e}", err=True)
                    raise typer.Exit(1)

            # Make files executable if specified
            import stat
            for file_path in executable_files:
                full_path = lang_output_dir / file_path
                if full_path.exists():
                    # Add executable permissions
                    full_path.chmod(full_path.stat().st_mode | stat.S_IEXEC)
                    logger.info(f"Made executable: {full_path}")
                    typer.echo(f"🔧 Made executable: {file_path}")

        # Manifest updating logic (only for certain languages that need it)
        languages_needing_manifests = [lang for lang in target_languages if lang in ["nodejs", "rust"]]
        
        if languages_needing_manifests:
            typer.echo("📦 Updating package manifests...")
            
        for language in languages_needing_manifests:
            # Determine manifest output directory
            if len(target_languages) > 1:
                manifest_output_dir = output_dir / language
            else:
                manifest_output_dir = output_dir
            
            # Always run the manifest updater - it will intelligently handle
            # both new files and existing files
            from goobits_cli.manifest_updater import update_manifests_for_build
            
            # Get CLI output path from configuration
            if language == "nodejs":
                # Use the actual configured CLI path or default
                cli_path_str = goobits_config.cli_path or "cli.mjs"
                # Transform Python extension to Node.js if needed
                if cli_path_str.endswith('.py'):
                    cli_path_str = cli_path_str.replace('.py', '.mjs')
                cli_path = Path(cli_path_str)
            else:
                # Rust - use configured path or default
                cli_path = Path(goobits_config.cli_path or "src/main.rs")
                
            manifest_file = "package.json" if language == "nodejs" else "Cargo.toml"
            
            manifest_result = update_manifests_for_build(
                config=goobits_config.model_dump(),
                output_dir=manifest_output_dir,
                cli_path=cli_path
            )
            
            if manifest_result.is_err():
                typer.echo(f"⚠️  Warning: {manifest_result.err()}", err=True)
                typer.echo("✅ CLI generated successfully, but manifest update failed")
            else:
                typer.echo(f"✅ Updated {manifest_file} with CLI configuration")
            
            # Display any warnings from the manifest update
            warnings = manifest_result.value or []
            for warning in warnings:
                typer.echo(f"⚠️  {warning}", err=True)

    logger.info("Build operation completed successfully")
    typer.echo("🎉 Build completed successfully!")

    # Clear operation context
    clear_context()