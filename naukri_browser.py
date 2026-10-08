from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from relevance import analyze_job
from question_answerer import answer_question
from excel_tracker import (
    prepare_real_tracker,
    save_application,
    save_skipped_job,
)


# ============================================================
# SETTINGS
# ============================================================

MAX_JOBS = 50


# ============================================================
# URL HELPERS
# ============================================================

def is_naukri_url(url):
    """Return True if the URL belongs to Naukri."""

    if not url:
        return False

    try:
        hostname = urlparse(url).hostname or ""
        hostname = hostname.lower()

        return (
            hostname == "naukri.com"
            or hostname.endswith(".naukri.com")
        )

    except Exception:
        return False


# ============================================================
# SEARCH JOBS
# ============================================================

def search_jobs(page):

    print("\nOpening Naukri...")

    page.goto(
        "https://www.naukri.com/mnjuser/homepage",
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(3000)

    print("Naukri opened.")

    # --------------------------------------------------------
    # SEARCH AREA
    # --------------------------------------------------------

    search_area = page.locator(
        "xpath=//*[@class='nI-gNb-sb__expand']"
    )

    search_area.click()

    print("Search area clicked.")

    # --------------------------------------------------------
    # SEARCH INPUT
    # --------------------------------------------------------

    search_input = page.locator(
        "xpath=(//*[@class='suggestor-input '])[1]"
    )

    search_input.fill("AI Engineer")

    print("AI Engineer entered.")

    # --------------------------------------------------------
    # SEARCH BUTTON
    # --------------------------------------------------------

    search_button = page.locator(
        "xpath=(//*[@class='ni-gnb-icn ni-gnb-icn-search'])[1]"
    )

    search_button.click()

    print("Search button clicked.")

    page.wait_for_timeout(5000)

    print("Search results loaded.")
    print("URL:", page.url)

    # --------------------------------------------------------
    # SORT BY DATE
    # --------------------------------------------------------

    sort_jobs_by_date(page)


# ============================================================
# SORT BY DATE
# ============================================================

def sort_jobs_by_date(page):

    print("\nLooking for sorting option...")

    page.wait_for_timeout(2000)

    selectors = [
        "text=Sort by",
        "text=Sort",
        "[class*='sort']",
        "[class*='Sort']",
    ]

    sort_element = None

    for selector in selectors:

        try:

            locator = page.locator(selector).first

            if locator.is_visible(timeout=1000):

                sort_element = locator

                break

        except Exception:
            continue

    if not sort_element:

        print(
            "⚠️ Sort option not found."
        )

        print(
            "Continuing with current Naukri order."
        )

        return

    try:

        sort_element.click()

        page.wait_for_timeout(1000)

    except Exception as error:

        print(
            "⚠️ Could not open sort menu:",
            error,
        )

        return

    date_selectors = [
        "text=Date",
        "text=Latest",
        "text=Newest",
        "text=Newest First",
        "text=Date Posted",
    ]

    for selector in date_selectors:

        try:

            option = page.locator(
                selector
            ).first

            if option.is_visible(timeout=1000):

                option.click()

                page.wait_for_timeout(3000)

                print(
                    "✅ Sorted by date / newest jobs."
                )

                return

        except Exception:
            continue

    print(
        "⚠️ Date sorting option was not found."
    )

    print(
        "Continuing with current order."
    )


# ============================================================
# EXTRACT JOBS
# ============================================================

def extract_jobs(page):

    print("\nExtracting jobs...")

    print(
        f"Target: {MAX_JOBS} unique jobs"
    )

    job_selectors = [
        "div.srp-jobtuple-wrapper",
        "article.jobTuple",
        "div.jobTuple",
        "div.cust-job-tuple",
    ]

    jobs_by_url = {}

    no_growth_count = 0

    while len(jobs_by_url) < MAX_JOBS:

        job_elements = None

        # ----------------------------------------------------
        # FIND CURRENT JOB CARDS
        # ----------------------------------------------------

        for selector in job_selectors:

            try:

                locator = page.locator(
                    selector
                )

                if locator.count() > 0:

                    job_elements = locator

                    break

            except Exception:
                continue

        if not job_elements:

            print(
                "❌ No job cards found."
            )

            break

        old_count = len(jobs_by_url)

        # ----------------------------------------------------
        # READ JOB CARDS
        # ----------------------------------------------------

        for index in range(
            job_elements.count()
        ):

            if len(jobs_by_url) >= MAX_JOBS:
                break

            try:

                job_element = (
                    job_elements.nth(index)
                )

                title = ""
                company = ""
                description = ""
                url = ""

                # ------------------------------------------------
                # TITLE
                # ------------------------------------------------

                for selector in [
                    "a.title",
                    "a[class*='title']",
                    "h2 a",
                    "h3 a",
                ]:

                    try:

                        locator = (
                            job_element
                            .locator(selector)
                            .first
                        )

                        if locator.count() > 0:

                            title = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if title:
                                break

                    except Exception:
                        continue

                # ------------------------------------------------
                # COMPANY
                # ------------------------------------------------

                for selector in [
                    "a.comp-name",
                    "a[class*='comp']",
                    "[class*='company']",
                ]:

                    try:

                        locator = (
                            job_element
                            .locator(selector)
                            .first
                        )

                        if locator.count() > 0:

                            company = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if company:
                                break

                    except Exception:
                        continue

                # ------------------------------------------------
                # DESCRIPTION
                # ------------------------------------------------

                for selector in [
                    ".job-desc",
                    "[class*='job-desc']",
                    "[class*='jobDescription']",
                ]:

                    try:

                        locator = (
                            job_element
                            .locator(selector)
                            .first
                        )

                        if locator.count() > 0:

                            description = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if description:
                                break

                    except Exception:
                        continue

                # ------------------------------------------------
                # URL
                # ------------------------------------------------

                for selector in [
                    "a.title",
                    "a[class*='title']",
                    "h2 a",
                    "h3 a",
                ]:

                    try:

                        locator = (
                            job_element
                            .locator(selector)
                            .first
                        )

                        if locator.count() > 0:

                            href = (
                                locator
                                .get_attribute("href")
                            )

                            if href:

                                url = href

                                if url.startswith(
                                    "/"
                                ):

                                    url = (
                                        "https://www.naukri.com"
                                        + url
                                    )

                                break

                    except Exception:
                        continue

                # ------------------------------------------------
                # REQUIRE TITLE + URL
                # ------------------------------------------------

                if not title:
                    continue

                if not url:
                    continue

                # ------------------------------------------------
                # DEDUPLICATE
                # ------------------------------------------------

                if url not in jobs_by_url:

                    jobs_by_url[url] = {
                        "title": title,
                        "company": company,
                        "description": description,
                        "url": url,
                    }

                    print(
                        f"{len(jobs_by_url)}. "
                        f"{title} | {company}"
                    )

            except Exception as error:

                print(
                    f"⚠️ Could not read job "
                    f"{index + 1}: {error}"
                )

        # ----------------------------------------------------
        # CHECK GROWTH
        # ----------------------------------------------------

        new_count = (
            len(jobs_by_url) - old_count
        )

        if new_count > 0:

            print(
                f"Loaded {new_count} new job(s). "
                f"Total: "
                f"{len(jobs_by_url)}/{MAX_JOBS}"
            )

            no_growth_count = 0

        else:

            no_growth_count += 1

            print(
                "No new jobs loaded. "
                f"Attempt {no_growth_count}/3"
            )

        if len(jobs_by_url) >= MAX_JOBS:
            break

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        try:

            previous_height = page.evaluate(
                "document.body.scrollHeight"
            )

            page.evaluate(
                """
                window.scrollTo(
                    0,
                    document.body.scrollHeight
                )
                """
            )

            page.wait_for_timeout(2500)

            current_height = page.evaluate(
                "document.body.scrollHeight"
            )

            print(
                "Scrolled:",
                previous_height,
                "→",
                current_height,
            )

        except Exception as error:

            print(
                "⚠️ Scroll failed:",
                error,
            )

            break

        # ----------------------------------------------------
        # LOAD MORE
        # ----------------------------------------------------

        load_more_selectors = [
            "button:has-text('Load More')",
            "button:has-text('View More')",
            "text=Load More",
            "text=View More",
        ]

        for selector in load_more_selectors:

            try:

                button = page.locator(
                    selector
                ).first

                if button.is_visible(
                    timeout=500
                ):

                    button.click()

                    page.wait_for_timeout(2500)

                    print(
                        "Clicked Load More."
                    )

                    break

            except Exception:
                continue

        # ----------------------------------------------------
        # STOP IF NO GROWTH
        # ----------------------------------------------------

        if no_growth_count >= 3:

            print(
                "\nNo additional jobs are loading."
            )

            break

    jobs = list(
        jobs_by_url.values()
    )[:MAX_JOBS]

    print(
        f"\nTotal unique jobs collected: "
        f"{len(jobs)}"
    )

    return jobs


# ============================================================
# AI ANALYSIS
# ============================================================

def analyze_jobs(jobs):

    print(
        "\nAnalyzing jobs with AI..."
    )

    results = []

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        print(
            f"\n[{index}/{len(jobs)}] "
            f"{job['title']} | "
            f"{job['company']}"
        )

        try:

            analysis = analyze_job(job)

            result = {
                "job": job,
                "analysis": analysis,
            }

            results.append(result)

            print(
                "Decision:",
                analysis["decision"],
            )

            print(
                "Match:",
                analysis["match_score"],
                "%",
            )

            print(
                "Reason:",
                analysis["reason"],
            )

            # ------------------------------------------------
            # SAVE SKIPS
            # ------------------------------------------------

            if (
                analysis["decision"]
                == "SKIP"
            ):

                save_skipped_job(
                    job,
                    analysis,
                    reason=analysis.get(
                        "reason",
                        "Job is not relevant",
                    ),
                )

        except Exception as error:

            print(
                "❌ AI analysis failed:",
                error,
            )

            save_application(
                job=job,
                analysis={
                    "decision": "UNKNOWN",
                    "match_score": "",
                    "reason": str(error),
                },
                status="ANALYSIS_FAILED",
                current_url="",
                external_url="",
                reason="AI analysis failed",
                notes=str(error),
            )

    return results


# ============================================================
# FIND APPLY BUTTON
# ============================================================

def find_apply_button(page):

    selectors = [
        "button:has-text('Apply')",
        "a:has-text('Apply')",
        "[class*='apply']:has-text('Apply')",
    ]

    for selector in selectors:

        try:

            buttons = page.locator(
                selector
            )

            count = buttons.count()

            for index in range(count):

                button = buttons.nth(index)

                if button.is_visible():

                    return button

        except Exception:
            continue

    return None


# ============================================================
# FORM DETECTION
# ============================================================

def detect_application_form(page):

    try:

        visible_inputs = page.locator(
            "input:visible"
        ).count()

        visible_textareas = page.locator(
            "textarea:visible"
        ).count()

        visible_selects = page.locator(
            "select:visible"
        ).count()

        total_fields = (
            visible_inputs
            + visible_textareas
            + visible_selects
        )

        return total_fields > 0

    except Exception:

        return False


# ============================================================
# GET FORM QUESTIONS
# ============================================================

def get_form_questions(page):

    questions = []

    try:

        fields = page.locator(
            "input:visible, "
            "textarea:visible, "
            "select:visible"
        )

        field_count = fields.count()

        print(
            f"Visible form fields: {field_count}"
        )

        for index in range(
            field_count
        ):

            field = fields.nth(index)

            try:

                field_type = (
                    field.get_attribute("type")
                    or "text"
                ).lower()

                # Skip non-answer fields
                if field_type in [
                    "hidden",
                    "submit",
                    "button",
                    "file",
                    "reset",
                ]:

                    continue

                question = field.evaluate(
                    """
                    element => {

                        function clean(text) {
                            return (text || "")
                                .replace(/\\\\s+/g, " ")
                                .trim();
                        }

                        let text = clean(
                            element.getAttribute(
                                "aria-label"
                            )
                        );

                        if (text) return text;

                        if (element.id) {

                            const label =
                                document.querySelector(
                                    `label[for="${element.id}"]`
                                );

                            if (label) {

                                text = clean(
                                    label.innerText
                                );

                                if (text) {
                                    return text;
                                }
                            }
                        }

                        const parentLabel =
                            element.closest("label");

                        if (parentLabel) {

                            text = clean(
                                parentLabel.innerText
                            );

                            if (text) {
                                return text;
                            }
                        }

                        text = clean(
                            element.getAttribute(
                                "placeholder"
                            )
                        );

                        if (text) return text;

                        text = clean(
                            element.getAttribute(
                                "name"
                            )
                        );

                        if (text) return text;

                        let parent =
                            element.parentElement;

                        for (
                            let i = 0;
                            i < 3 && parent;
                            i++
                        ) {

                            text = clean(
                                parent.innerText
                            );

                            if (
                                text &&
                                text.length < 500
                            ) {

                                return text;
                            }

                            parent =
                                parent.parentElement;
                        }

                        return "";
                    }
                    """
                )

                if question:

                    questions.append(
                        {
                            "index": index,
                            "question": question,
                            "field": field,
                            "type": field_type,
                        }
                    )

            except Exception as error:

                print(
                    f"⚠️ Could not read "
                    f"form field {index}: "
                    f"{error}"
                )

    except Exception as error:

        print(
            "❌ Could not inspect form:",
            error,
        )

    return questions


# ============================================================
# HANDLE APPLICATION FORM
# ============================================================

def handle_application_form(
    page,
    job,
    analysis,
):

    print(
        "\n📝 Inspecting application form..."
    )

    questions = get_form_questions(page)

    if not questions:

        print(
            "⚠️ Form detected, "
            "but no readable questions found."
        )

        save_application(
            job=job,
            analysis=analysis,
            status="FORM_UNANSWERED",
            current_url=page.url,
            reason=(
                "Application form could not "
                "be read."
            ),
            notes="Manual review required.",
        )

        return {
            "status": "FORM_UNANSWERED",
            "question": "",
        }

    print(
        f"Found {len(questions)} "
        f"readable form field(s)."
    )

    for item in questions:

        question = item["question"]
        field = item["field"]
        field_type = item["type"]

        print(
            "\nQuestion:"
        )

        print(
            question
        )

        # ----------------------------------------------------
        # ASK QUESTION ANSWERER
        # ----------------------------------------------------

        try:

            result = answer_question(
                question
            )

        except Exception as error:

            print(
                "❌ Question answerer failed:",
                error,
            )

            save_application(
                job=job,
                analysis=analysis,
                status="FORM_UNANSWERED",
                current_url=page.url,
                reason=(
                    "Question answerer failed."
                ),
                notes=str(error),
                unanswered_question=question,
            )

            return {
                "status": "FORM_UNANSWERED",
                "question": question,
            }

        answer = result.get(
            "answer",
            "",
        )

        status = result.get(
            "status",
            "UNKNOWN",
        )

        print(
            "Answer:",
            answer,
        )

        print(
            "Status:",
            status,
        )

        # ----------------------------------------------------
        # UNKNOWN = NEVER GUESS
        # ----------------------------------------------------

        if (
            status != "KNOWN"
            or not answer
        ):

            print(
                "\n⚠️ Cannot answer "
                "this question safely."
            )

            print(
                "Application will NOT "
                "be submitted."
            )

            save_application(
                job=job,
                analysis=analysis,
                status="FORM_UNANSWERED",
                current_url=page.url,
                reason=(
                    "Question cannot be answered "
                    "from candidate profile."
                ),
                notes=(
                    "Agent stopped this application "
                    "instead of guessing."
                ),
                unanswered_question=question,
            )

            return {
                "status": "FORM_UNANSWERED",
                "question": question,
            }

        # ----------------------------------------------------
        # TEXT INPUTS
        # ----------------------------------------------------

        try:

            if field_type in [
                "text",
                "email",
                "tel",
                "number",
                "url",
                "search",
            ]:

                field.fill(
                    str(answer)
                )

                print(
                    "✅ Field filled."
                )

            # ------------------------------------------------
            # TEXTAREA
            # ------------------------------------------------

            elif field_type == "textarea":

                field.fill(
                    str(answer)
                )

                print(
                    "✅ Textarea filled."
                )

            # ------------------------------------------------
            # SELECT
            # ------------------------------------------------

            elif field_type == "select":

                options = field.locator(
                    "option"
                )

                matched = False

                for option_index in range(
                    options.count()
                ):

                    option = options.nth(
                        option_index
                    )

                    option_text = (
                        option
                        .inner_text()
                        .strip()
                    )

                    if (
                        option_text.lower()
                        == str(answer)
                        .strip()
                        .lower()
                    ):

                        value = (
                            option
                            .get_attribute(
                                "value"
                            )
                        )

                        if value is not None:

                            field.select_option(
                                value=value
                            )

                            matched = True

                            print(
                                "✅ Select "
                                "field filled."
                            )

                            break

                if not matched:

                    print(
                        "⚠️ Could not safely "
                        "match select option."
                    )

                    save_application(
                        job=job,
                        analysis=analysis,
                        status="FORM_UNANSWERED",
                        current_url=page.url,
                        reason=(
                            "Could not safely match "
                            "the answer to a form option."
                        ),
                        notes=(
                            f"Question: {question}"
                        ),
                        unanswered_question=question,
                    )

                    return {
                        "status": "FORM_UNANSWERED",
                        "question": question,
                    }

            # ------------------------------------------------
            # UNSUPPORTED FIELD
            # ------------------------------------------------

            else:

                print(
                    f"⚠️ Unsupported field type: "
                    f"{field_type}"
                )

                save_application(
                    job=job,
                    analysis=analysis,
                    status="FORM_UNANSWERED",
                    current_url=page.url,
                    reason=(
                        "Form field type is "
                        "not currently supported."
                    ),
                    notes=(
                        f"Field type: {field_type}"
                    ),
                    unanswered_question=question,
                )

                return {
                    "status": "FORM_UNANSWERED",
                    "question": question,
                }

        except Exception as error:

            print(
                "❌ Could not fill field:",
                error,
            )

            save_application(
                job=job,
                analysis=analysis,
                status="FORM_UNANSWERED",
                current_url=page.url,
                reason=(
                    "Could not fill "
                    "application field."
                ),
                notes=str(error),
                unanswered_question=question,
            )

            return {
                "status": "FORM_UNANSWERED",
                "question": question,
            }

    # --------------------------------------------------------
    # ALL QUESTIONS ANSWERED
    # --------------------------------------------------------

    print(
        "\n✅ All detected questions "
        "were answered."
    )

    return {
        "status": "FORM_READY",
        "question": "",
    }


# ============================================================
# EXTERNAL URL DETECTION
# ============================================================

def detect_external_page(
    page,
    pages_before,
):

    context = page.context

    # --------------------------------------------------------
    # SAME PAGE REDIRECT
    # --------------------------------------------------------

    try:

        if not is_naukri_url(
            page.url
        ):

            return {
                "external_url": page.url,
                "external_page": None,
            }

    except Exception:
        pass

    # --------------------------------------------------------
    # NEW TAB / WINDOW
    # --------------------------------------------------------

    current_pages = context.pages

    new_pages = [
        current_page
        for current_page in current_pages
        if current_page not in pages_before
    ]

    for new_page in new_pages:

        try:

            new_page.wait_for_timeout(
                2000
            )

            external_url = (
                new_page.url
            )

            if (
                external_url
                and not is_naukri_url(
                    external_url
                )
            ):

                return {
                    "external_url": external_url,
                    "external_page": new_page,
                }

        except Exception:
            continue

    return {
        "external_url": "",
        "external_page": None,
    }


# ============================================================
# APPLY TO ALL JOBS
# ============================================================

def apply_to_all_jobs(
    page,
    results,
):

    print(
        "\n"
        + "=" * 70
    )

    print(
        "STARTING APPLICATION PROCESS"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # SAVE RESULTS PAGE
    # --------------------------------------------------------

    results_page_url = page.url

    application_results = []

    # --------------------------------------------------------
    # ONLY APPLY JOBS
    # --------------------------------------------------------

    apply_results = [
        result
        for result in results
        if result["analysis"]["decision"]
        == "APPLY"
    ]

    print(
        f"\nJobs selected for application: "
        f"{len(apply_results)}"
    )

    # --------------------------------------------------------
    # LOOP JOBS
    # --------------------------------------------------------

    for index, result in enumerate(
        apply_results,
        start=1,
    ):

        job = result["job"]

        analysis = result["analysis"]

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"[{index}/{len(apply_results)}] "
            f"{job['title']} | "
            f"{job['company']}"
        )

        print(
            "Naukri URL:",
            job["url"],
        )

        # ----------------------------------------------------
        # MISSING URL
        # ----------------------------------------------------

        if not job.get("url"):

            print(
                "❌ Job URL missing."
            )

            save_application(
                job,
                analysis,
                status="NO_URL",
                reason=(
                    "Job URL was not found."
                ),
            )

            application_results.append(
                {
                    "job": job,
                    "status": "NO_URL",
                }
            )

            continue

        # ----------------------------------------------------
        # OPEN JOB
        # ----------------------------------------------------

        try:

            page.goto(
                job["url"],
                wait_until="domcontentloaded",
                timeout=60000,
            )

            page.wait_for_timeout(
                2500
            )

        except Exception as error:

            print(
                "❌ Could not open job:",
                error,
            )

            save_application(
                job,
                analysis,
                status="OPEN_FAILED",
                current_url=page.url,
                reason=(
                    "Could not open "
                    "Naukri job page."
                ),
                notes=str(error),
            )

            application_results.append(
                {
                    "job": job,
                    "status": "OPEN_FAILED",
                }
            )

            continue

        # ----------------------------------------------------
        # FIND APPLY BUTTON
        # ----------------------------------------------------

        apply_button = (
            find_apply_button(page)
        )

        if not apply_button:

            print(
                "⚠️ Apply button not found."
            )

            save_application(
                job,
                analysis,
                status="APPLY_BUTTON_NOT_FOUND",
                current_url=page.url,
                reason=(
                    "Apply button was not found."
                ),
            )

            application_results.append(
                {
                    "job": job,
                    "status": (
                        "APPLY_BUTTON_NOT_FOUND"
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # CLICK APPLY
        # ----------------------------------------------------

        print(
            "🚀 Clicking Apply..."
        )

        pages_before = list(
            page.context.pages
        )

        try:

            apply_button.click()

            page.wait_for_timeout(
                4000
            )

        except Exception as error:

            print(
                "❌ Apply click failed:",
                error,
            )

            save_application(
                job,
                analysis,
                status="APPLY_CLICK_FAILED",
                current_url=page.url,
                reason=(
                    "Could not click Apply."
                ),
                notes=str(error),
            )

            application_results.append(
                {
                    "job": job,
                    "status": (
                        "APPLY_CLICK_FAILED"
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # EXTERNAL APPLICATION
        # ----------------------------------------------------

        external_result = (
            detect_external_page(
                page,
                pages_before,
            )
        )

        external_url = (
            external_result[
                "external_url"
            ]
        )

        external_page = (
            external_result[
                "external_page"
            ]
        )

        if external_url:

            print(
                "\n🌐 EXTERNAL "
                "APPLICATION DETECTED"
            )

            print(
                "External URL:",
                external_url,
            )

            save_application(
                job=job,
                analysis=analysis,
                status=(
                    "EXTERNAL_APPLICATION"
                ),
                current_url=page.url,
                external_url=external_url,
                reason=(
                    "Apply redirected to "
                    "an external company "
                    "application page."
                ),
                notes=(
                    "Manual application "
                    "required on external "
                    "website."
                ),
            )

            application_results.append(
                {
                    "job": job,
                    "status": (
                        "EXTERNAL_APPLICATION"
                    ),
                    "external_url": (
                        external_url
                    ),
                }
            )

            # ------------------------------------------------
            # CLOSE EXTERNAL TAB
            # ------------------------------------------------

            if external_page:

                try:

                    external_page.close()

                    print(
                        "External page closed."
                    )

                except Exception:
                    pass

            # ------------------------------------------------
            # RETURN TO NAUKRI
            # ------------------------------------------------

            if not is_naukri_url(
                page.url
            ):

                try:

                    page.goto(
                        results_page_url,
                        wait_until=(
                            "domcontentloaded"
                        ),
                        timeout=60000,
                    )

                    page.wait_for_timeout(
                        2500
                    )

                    print(
                        "↩️ Returned to Naukri."
                    )

                except Exception as error:

                    print(
                        "⚠️ Could not return "
                        "to Naukri:",
                        error,
                    )

            continue

        # ----------------------------------------------------
        # CHECK APPLICATION FORM
        # ----------------------------------------------------

        if detect_application_form(
            page
        ):

            print(
                "📝 Naukri application "
                "form detected."
            )

            form_result = (
                handle_application_form(
                    page,
                    job,
                    analysis,
                )
            )

            form_status = (
                form_result["status"]
            )

            application_results.append(
                {
                    "job": job,
                    "status": form_status,
                    "question": (
                        form_result.get(
                            "question",
                            "",
                        )
                    ),
                }
            )

            # ------------------------------------------------
            # UNKNOWN QUESTION
            # ------------------------------------------------

            if (
                form_status
                == "FORM_UNANSWERED"
            ):

                print(
                    "\n⏭️ Cannot safely "
                    "complete this application."
                )

                print(
                    "Moving to next job..."
                )

                continue

            # ------------------------------------------------
            # ALL ANSWERS FILLED
            # ------------------------------------------------

            if (
                form_status
                == "FORM_READY"
            ):

                print(
                    "\n✅ Form fields "
                    "were filled."
                )

                print(
                    "⚠️ Submit is NOT "
                    "automated yet."
                )

                save_application(
                    job=job,
                    analysis=analysis,
                    status="FORM_READY",
                    current_url=page.url,
                    reason=(
                        "All detected form "
                        "questions were "
                        "answered from "
                        "the profile."
                    ),
                    notes=(
                        "Form filled. "
                        "Submit action is "
                        "not automated yet."
                    ),
                )

                continue

        # ----------------------------------------------------
        # NO FORM
        # ----------------------------------------------------

        print(
            "✅ Naukri application "
            "request completed."
        )

        print(
            "Current URL:",
            page.url,
        )

        save_application(
            job=job,
            analysis=analysis,
            status="APPLIED",
            current_url=page.url,
            external_url="",
            reason=(
                "Naukri Apply action "
                "completed without "
                "an application form."
            ),
            notes=(
                "Application submitted "
                "through Naukri."
            ),
        )

        application_results.append(
            {
                "job": job,
                "status": "APPLIED",
            }
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "APPLICATION SUMMARY"
    )

    print(
        "=" * 70
    )

    counts = {}

    for result in application_results:

        status = result["status"]

        counts[status] = (
            counts.get(status, 0)
            + 1
        )

    for status, count in counts.items():

        print(
            f"{status}: {count}"
        )

    print(
        "=" * 70
    )

    return application_results


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # CLEAN TEST ROWS
    # --------------------------------------------------------

    prepare_real_tracker()

    # --------------------------------------------------------
    # PLAYWRIGHT
    # --------------------------------------------------------

    with sync_playwright() as p:

        print(
            "\nLaunching persistent "
            "Naukri browser..."
        )

        context = (
            p.chromium.launch_persistent_context(
                user_data_dir="naukri_session",
                headless=False,
            )
        )

        # ----------------------------------------------------
        # GET PAGE
        # ----------------------------------------------------

        if context.pages:

            page = context.pages[0]

        else:

            page = context.new_page()

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_jobs(page)

        # ----------------------------------------------------
        # EXTRACT UP TO 50
        # ----------------------------------------------------

        jobs = extract_jobs(page)

        if not jobs:

            print(
                "\n❌ No jobs found."
            )

            context.close()

            return

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        results = analyze_jobs(
            jobs
        )

        # ----------------------------------------------------
        # APPLY
        # ----------------------------------------------------

        application_results = (
            apply_to_all_jobs(
                page,
                results,
            )
        )

        # ----------------------------------------------------
        # FINAL SUMMARY
        # ----------------------------------------------------

        print(
            "\n"
            + "=" * 70
        )

        print(
            "FINAL RUN COMPLETED"
        )

        print(
            "=" * 70
        )

        print(
            f"Jobs discovered: "
            f"{len(jobs)}"
        )

        print(
            f"Jobs analyzed: "
            f"{len(results)}"
        )

        print(
            f"Application actions: "
            f"{len(application_results)}"
        )

        print(
            "\nExcel tracker:"
        )

        print(
            "application_tracker.xlsx"
        )

        print(
            "=" * 70
        )

        print(
            "\nBrowser will remain open."
        )

        input(
            "\nPress ENTER to close "
            "the browser..."
        )

        context.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

    # python naukri_browser.py