from question_answerer import answer_question


def get_field_question(field):
    """
    Try to determine what question/label belongs to a form field.
    """

    # Placeholder
    placeholder = (
        field.get_attribute("placeholder")
        or ""
    ).strip()

    if placeholder:
        return placeholder

    # aria-label
    aria_label = (
        field.get_attribute("aria-label")
        or ""
    ).strip()

    if aria_label:
        return aria_label

    # name
    name = (
        field.get_attribute("name")
        or ""
    ).strip()

    if name:
        return name

    # id
    field_id = (
        field.get_attribute("id")
        or ""
    ).strip()

    if field_id:
        return field_id

    return ""


def inspect_application_form(page):

    print("\n" + "=" * 70)
    print("INSPECTING APPLICATION FORM")
    print("=" * 70)

    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    inputs = page.locator("input")

    input_count = inputs.count()

    print(
        "\nInput fields found:",
        input_count
    )

    for i in range(input_count):

        field = inputs.nth(i)

        try:

            if not field.is_visible():
                continue

            field_type = (
                field.get_attribute("type")
                or "text"
            )

            # Skip hidden fields
            if field_type in [
                "hidden",
                "submit",
                "button"
            ]:
                continue

            question = get_field_question(field)

            print("\n" + "-" * 50)

            print(
                f"FIELD {i + 1}"
            )

            print(
                "Type:",
                field_type
            )

            print(
                "Question:",
                question
            )

            # ------------------------------------------------
            # Ask AI for answer
            # ------------------------------------------------

            if question:

                result = answer_question(
                    question
                )

                answer = result.get(
                    "answer",
                    ""
                )

                status = result.get(
                    "status",
                    "UNKNOWN"
                )

                print(
                    "AI Answer:",
                    answer
                )

                print(
                    "Status:",
                    status
                )

                # ------------------------------------------------
                # We DO NOT fill yet.
                # ------------------------------------------------

                if status == "KNOWN":

                    print(
                        "→ Known answer found."
                    )

                else:

                    print(
                        "→ Unknown answer."
                    )

        except Exception as error:

            print(
                f"Could not process "
                f"field {i + 1}: {error}"
            )

    # --------------------------------------------------------
    # TEXTAREAS
    # --------------------------------------------------------

    textareas = page.locator("textarea")

    textarea_count = textareas.count()

    print(
        "\n" + "=" * 70
    )

    print(
        "Textareas found:",
        textarea_count
    )

    for i in range(textarea_count):

        field = textareas.nth(i)

        try:

            if not field.is_visible():
                continue

            question = get_field_question(
                field
            )

            print("\n" + "-" * 50)

            print(
                f"TEXTAREA {i + 1}"
            )

            print(
                "Question:",
                question
            )

            if question:

                result = answer_question(
                    question
                )

                print(
                    "AI Answer:",
                    result.get(
                        "answer",
                        ""
                    )
                )

                print(
                    "Status:",
                    result.get(
                        "status",
                        "UNKNOWN"
                    )
                )

        except Exception as error:

            print(
                f"Could not process "
                f"textarea {i + 1}: {error}"
            )

    # --------------------------------------------------------
    # SELECT / DROPDOWN
    # --------------------------------------------------------

    selects = page.locator("select")

    select_count = selects.count()

    print(
        "\n" + "=" * 70
    )

    print(
        "Dropdowns found:",
        select_count
    )

    for i in range(select_count):

        field = selects.nth(i)

        try:

            if not field.is_visible():
                continue

            question = get_field_question(
                field
            )

            print("\n" + "-" * 50)

            print(
                f"DROPDOWN {i + 1}"
            )

            print(
                "Question:",
                question
            )

            # Show options

            options = field.locator(
                "option"
            )

            option_count = options.count()

            print(
                "Options:"
            )

            for j in range(option_count):

                option = options.nth(j)

                option_text = (
                    option.inner_text()
                    .strip()
                )

                if option_text:

                    print(
                        "  -",
                        option_text
                    )

            if question:

                result = answer_question(
                    question
                )

                print(
                    "AI Answer:",
                    result.get(
                        "answer",
                        ""
                    )
                )

                print(
                    "Status:",
                    result.get(
                        "status",
                        "UNKNOWN"
                    )
                )

        except Exception as error:

            print(
                f"Could not process "
                f"dropdown {i + 1}: {error}"
            )

    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    buttons = page.locator("button")

    button_count = buttons.count()

    print(
        "\n" + "=" * 70
    )

    print(
        "Buttons found:",
        button_count
    )

    for i in range(button_count):

        button = buttons.nth(i)

        try:

            if not button.is_visible():
                continue

            text = (
                button.inner_text()
                .strip()
            )

            if text:

                print(
                    f"BUTTON {i + 1}:",
                    text
                )

        except Exception:
            pass

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "APPLICATION FORM ANALYSIS COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        "\nForm filling is NOT enabled yet."
    )

    print(
        "Submit is NOT enabled yet."
    )
    