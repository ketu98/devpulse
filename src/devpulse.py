
    if (
        topic
        not in state.get(
            "used_topics",
            []
        )
    ):

        state.setdefault(
            "used_topics",
            []
        ).append(
            topic
        )

    save_json(
        DATA
        / "state.json",
        state
    )

    # --------------------------------------------------------
    # COMMIT MESSAGE
    # --------------------------------------------------------

    (
        ROOT
        / ".devpulse_commit_message"
    ).write_text(
        metadata[
            "commit_message"
        ].strip(),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # MANIFEST FOR THIS RUN ONLY
    # --------------------------------------------------------

    manifest = {
        "generated":
            True,

        "category":
            category,

        "topic":
            topic,

        "title":
            title,

        "slug":
            slug,

        "linkedin_file":
            (
                linkedin_file
                .relative_to(
                    ROOT
                )
                .as_posix()
            ),

        "image_file":
            (
                image_path
                .relative_to(
                    ROOT
                )
                .as_posix()
            ),

        "github_poc_url":
            github_poc_url
    }

    MANIFEST.write_text(
        json.dumps(
            manifest,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Generated package: "
        f"{base}"
    )

    print(
        f"LinkedIn file: "
        f"{linkedin_file}"
    )

    print(
        f"Diagram: "
        f"{image_path}"
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
